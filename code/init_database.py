#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
832工程数据库初始化脚本
将CSV数据导入MySQL数据库
"""

import pandas as pd
import pymysql
import numpy as np
from pathlib import Path
import sys

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # 请修改为实际密码
    'database': 'poverty_alleviation_832',
    'charset': 'utf8mb4'
}

# 数据目录路径（相对于脚本所在位置，向上两级到项目根目录）
DATA_DIR = Path(__file__).parent.parent / 'data'


def get_db_connection():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG)


def clean_value(val):
    """清洗数据值，处理NaN和空值"""
    if pd.isna(val) or val == '' or val == '—' or str(val).strip() == '':
        return None
    return val


def to_float64(val):
    """转换为float64，处理NaN"""
    if pd.isna(val) or val == '' or val == '—':
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def to_int(val):
    """转换为int，处理NaN"""
    if pd.isna(val) or val == '' or val == '—':
        return None
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return None


def collect_all_county_codes():
    """从所有CSV文件中收集县代码"""
    county_codes = set()
    
    csv_files = [
        ('county_profile.csv', 'CountyCode'),
        ('county_relief.csv', '行政区划代码'),
        ('poverty_county_list.csv', '行政区划代码'),
        ('county_agri_output.csv', '县域代码'),
        ('county_crop_area.csv', '县域代码'),
        ('county_finance_budget_raw.csv', 'CountyCode'),
        ('county_transport_post.csv', 'CountyCode'),
        ('county_financial_services.csv', 'CountyCode'),
        ('county_gdp.csv', 'CountyCode'),
        ('county_income.csv', 'CountyCode'),
        ('county_population.csv', 'CountyCode'),
        ('interviews.csv', '县id'),
        ('surveyors.csv', '负责县域ID'),
    ]
    
    for filename, colname in csv_files:
        try:
            filepath = DATA_DIR / filename
            if not filepath.exists():
                continue
            
            try:
                test_df = pd.read_csv(filepath, nrows=0)
                if colname not in test_df.columns:
                    continue
            except:
                continue
            
            df = pd.read_csv(filepath, dtype={colname: str}, low_memory=False)
            if colname in df.columns:
                codes = df[colname].dropna()
                codes_clean = []
                for code in codes:
                    try:
                        code_int = int(float(code))
                        codes_clean.append(str(code_int).zfill(6)[:6])
                    except (ValueError, TypeError):
                        code_str = str(code).replace('.0', '').replace('.', '')
                        codes_clean.append(code_str.zfill(6)[:6])
                codes_unique = list(set(codes_clean))
                county_codes.update(codes_unique)
                print(f"  从 {filename} 收集到 {len(codes_unique)} 个县代码")
        except Exception as e:
            print(f"  读取 {filename} 时出错: {e}")
    
    return county_codes


def import_county_table(conn):
    """导入county表"""
    print("导入county表...")
    print("收集所有CSV文件中的县代码...")
    all_county_codes = collect_all_county_codes()
    print(f"共收集到 {len(all_county_codes)} 个唯一的县代码")
    
    df = pd.read_csv(DATA_DIR / 'county_profile.csv', dtype={'CountyCode': str}, low_memory=False)
    df_county = df.groupby('CountyCode').first().reset_index()
    
    cursor = conn.cursor()
    inserted = 0
    inserted_minimal = 0
    
    for _, row in df_county.iterrows():
        try:
            county_code = str(row['CountyCode']).zfill(6)
            sql = """
                INSERT INTO county (CountyCode, CountyName, Province, City, Longitude, Latitude, 
                                   LandArea, TownshipCount, VillageCount)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    CountyName=VALUES(CountyName), Province=VALUES(Province), City=VALUES(City),
                    Longitude=VALUES(Longitude), Latitude=VALUES(Latitude),
                    LandArea=VALUES(LandArea), TownshipCount=VALUES(TownshipCount),
                    VillageCount=VALUES(VillageCount)
            """
            cursor.execute(sql, (
                county_code, clean_value(row.get('地区名称')), clean_value(row.get('所属省份')),
                clean_value(row.get('所属城市')), to_float64(row.get('经度')),
                to_float64(row.get('纬度')), to_float64(row.get('行政区域土地面积(平方公里)')),
                to_int(row.get('乡及镇个数(个)')), to_int(row.get('乡个数(个)'))
            ))
            inserted += 1
        except Exception as e:
            print(f"导入county表错误 (CountyCode={row.get('CountyCode')}): {e}")
    
    cursor.execute("SELECT CountyCode FROM county")
    existing_codes = {row[0] for row in cursor.fetchall()}
    missing_codes = all_county_codes - existing_codes
    
    if missing_codes:
        print(f"发现 {len(missing_codes)} 个缺失的县代码，正在补充...")
        for county_code in missing_codes:
            try:
                county_code_clean = str(county_code)[:6].zfill(6)
                sql = "INSERT IGNORE INTO county (CountyCode, CountyName, Province, City) VALUES (%s, %s, %s, %s)"
                cursor.execute(sql, (county_code_clean, f'县代码{county_code_clean}', '未知', '未知'))
                inserted_minimal += 1
            except Exception as e:
                print(f"补充县代码失败 (CountyCode={county_code}): {e}")
    
    conn.commit()
    print(f"county表导入完成，共 {inserted} 条完整记录，{inserted_minimal} 条最小记录")
    cursor.close()


def import_county_nature(conn):
    """导入county_nature表"""
    print("导入county_nature表...")
    df = pd.read_csv(DATA_DIR / 'county_relief.csv', dtype={'行政区划代码': str}, low_memory=False)
    cursor = conn.cursor()
    inserted = 0
    
    for _, row in df.iterrows():
        try:
            county_code_raw = row['行政区划代码']
            if pd.notna(county_code_raw):
                try:
                    county_code = str(int(float(county_code_raw))).zfill(6)[:6]
                except (ValueError, TypeError):
                    county_code = str(county_code_raw).replace('.0', '').replace('.', '').zfill(6)[:6]
            else:
                continue
            sql = """
                INSERT INTO county_nature (CountyCode, RegionLevel, TerrainRelief, Longitude, Latitude)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    RegionLevel=VALUES(RegionLevel), TerrainRelief=VALUES(TerrainRelief),
                    Longitude=VALUES(Longitude), Latitude=VALUES(Latitude)
            """
            cursor.execute(sql, (
                county_code, to_int(row.get('地区等级')), to_float64(row.get('地形起伏度')),
                to_float64(row.get('经度')), to_float64(row.get('纬度'))
            ))
            inserted += 1
        except Exception as e:
            print(f"导入county_nature表错误: {e}")
    
    conn.commit()
    print(f"county_nature表导入完成，共 {inserted} 条记录")
    cursor.close()


def import_county_economy(conn):
    """导入county_economy表"""
    print("导入county_economy表...")
    df = pd.read_csv(DATA_DIR / 'county_profile.csv', dtype={'CountyCode': str}, low_memory=False)
    cursor = conn.cursor()
    inserted = 0
    
    def get_col_value(*possible_names):
        for name in possible_names:
            if name in row:
                return row[name]
        return None
    
    for _, row in df.iterrows():
        try:
            county_code = str(row['CountyCode']).zfill(6)
            year = to_int(row.get('年份'))
            if not year:
                continue
            
            sql = """
                INSERT INTO county_economy (
                    CountyCode, Year, GDP, GDP_Primary, GDP_Secondary, GDP_Tertiary,
                    PerCapitaGDP, UrbanAvgWage, RuralDisposableIncome,
                    FiscalRevenue, FiscalExpenditure, SavingsDeposit, LoanBalance,
                    IndustrialOutput, IndustrialEnterpriseCount, FixedAssetInvestment, RetailSales
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    GDP=VALUES(GDP), GDP_Primary=VALUES(GDP_Primary), GDP_Secondary=VALUES(GDP_Secondary),
                    GDP_Tertiary=VALUES(GDP_Tertiary), PerCapitaGDP=VALUES(PerCapitaGDP),
                    UrbanAvgWage=VALUES(UrbanAvgWage), RuralDisposableIncome=VALUES(RuralDisposableIncome),
                    FiscalRevenue=VALUES(FiscalRevenue), FiscalExpenditure=VALUES(FiscalExpenditure),
                    SavingsDeposit=VALUES(SavingsDeposit), LoanBalance=VALUES(LoanBalance),
                    IndustrialOutput=VALUES(IndustrialOutput), IndustrialEnterpriseCount=VALUES(IndustrialEnterpriseCount),
                    FixedAssetInvestment=VALUES(FixedAssetInvestment), RetailSales=VALUES(RetailSales)
            """
            cursor.execute(sql, (
                county_code, year,
                to_float64(get_col_value('地区生产总值(万元)\n—来源公众号【马克数据网】', '地区生产总值(万元)')),
                to_float64(row.get('第一产业增加值(万元)')), to_float64(row.get('第二产业增加值(万元)')),
                to_float64(row.get('第三产业增加值(万元)')), to_float64(row.get('人均地区生产总值(元/人)')),
                to_float64(row.get('城镇单位在岗职工平均工资(元)')),
                to_float64(get_col_value('农村居民人均可支配收入(元)\n—来源公众号【马克数据网】', '农村居民人均可支配收入(元)')),
                to_float64(row.get('地方财政一般预算收入(万元)')), to_float64(row.get('地方财政一般预算支出(万元)')),
                to_float64(row.get('城乡居民储蓄存款余额(万元)')), to_float64(row.get('年末金融机构各项贷款余额(万元)')),
                to_float64(row.get('规模以上工业总产值(万元)')), to_int(row.get('规模以上工业企业数(个)')),
                to_float64(row.get('全社会固定资产投资(万元)')), to_float64(row.get('社会消费品零售总额(万元)'))
            ))
            inserted += 1
        except Exception as e:
            print(f"导入county_economy表错误: {e}")
    
    conn.commit()
    print(f"county_economy表导入完成，共 {inserted} 条记录")
    cursor.close()


def import_county_agriculture(conn):
    """导入county_agriculture表"""
    print("导入county_agriculture表...")
    df = pd.read_csv(DATA_DIR / 'county_profile.csv', dtype={'CountyCode': str}, low_memory=False)
    cursor = conn.cursor()
    inserted = 0
    
    for _, row in df.iterrows():
        try:
            county_code = str(row['CountyCode']).zfill(6)
            year = to_int(row.get('年份'))
            if not year:
                continue
            sql = """
                INSERT INTO county_agriculture (
                    CountyCode, Year, CropArea, MachineryPower, GrainOutput,
                    CottonOutput, OilOutput, MeatOutput, AgriOutputValue,
                    RuralLaborForce, AgriLaborForce
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    CropArea=VALUES(CropArea), MachineryPower=VALUES(MachineryPower),
                    GrainOutput=VALUES(GrainOutput), CottonOutput=VALUES(CottonOutput),
                    OilOutput=VALUES(OilOutput), MeatOutput=VALUES(MeatOutput),
                    AgriOutputValue=VALUES(AgriOutputValue), RuralLaborForce=VALUES(RuralLaborForce),
                    AgriLaborForce=VALUES(AgriLaborForce)
            """
            cursor.execute(sql, (
                county_code, year, to_float64(row.get('农作物总播种面积(千公顷)')),
                to_float64(row.get('农用机械总动力(千万瓦)')), to_float64(row.get('粮食总产量(吨)')),
                to_float64(row.get('棉花产量(吨)')), to_float64(row.get('油料产量(吨)')),
                to_float64(row.get('肉类总产量(吨)')), to_float64(row.get('农林牧渔业总产值(万元)')),
                to_int(row.get('乡村从业人员数(人)')), to_int(row.get('农林牧渔业从业人员数(人)'))
            ))
            inserted += 1
        except Exception as e:
            print(f"导入county_agriculture表错误: {e}")
    
    conn.commit()
    print(f"county_agriculture表导入完成，共 {inserted} 条记录")
    cursor.close()


def import_county_population(conn):
    """导入county_population表"""
    print("导入county_population表...")
    df = pd.read_csv(DATA_DIR / 'county_profile.csv', dtype={'CountyCode': str}, low_memory=False)
    cursor = conn.cursor()
    inserted = 0
    
    for _, row in df.iterrows():
        try:
            county_code = str(row['CountyCode']).zfill(6)
            year = to_int(row.get('年份'))
            if not year:
                continue
            sql = """
                INSERT INTO county_population (
                    CountyCode, Year, RegisteredPopulation,
                    PrimarySchoolTeachers, MiddleSchoolTeachers,
                    PrimarySchoolStudents, MiddleSchoolStudents
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    RegisteredPopulation=VALUES(RegisteredPopulation),
                    PrimarySchoolTeachers=VALUES(PrimarySchoolTeachers),
                    MiddleSchoolTeachers=VALUES(MiddleSchoolTeachers),
                    PrimarySchoolStudents=VALUES(PrimarySchoolStudents),
                    MiddleSchoolStudents=VALUES(MiddleSchoolStudents)
            """
            cursor.execute(sql, (
                county_code, year, to_float64(row.get('户籍人口数(万人)')),
                to_int(row.get('普通小学专任教师数(人)')), to_int(row.get('普通中学专任教师数(人)')),
                to_int(row.get('普通小学在校生数(人)')), to_int(row.get('普通中学在校学生数(人)'))
            ))
            inserted += 1
        except Exception as e:
            print(f"导入county_population表错误: {e}")
    
    conn.commit()
    print(f"county_population表导入完成，共 {inserted} 条记录")
    cursor.close()


def import_county_healthcare(conn):
    """导入county_healthcare表"""
    print("导入county_healthcare表...")
    df = pd.read_csv(DATA_DIR / 'county_profile.csv', dtype={'CountyCode': str}, low_memory=False)
    cursor = conn.cursor()
    inserted = 0
    
    for _, row in df.iterrows():
        try:
            county_code = str(row['CountyCode']).zfill(6)
            year = to_int(row.get('年份'))
            if not year:
                continue
            sql = """
                INSERT INTO county_healthcare (
                    CountyCode, Year, HospitalBeds, MedicalPersonnel,
                    WelfareInstitutions, WelfareBeds
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    HospitalBeds=VALUES(HospitalBeds), MedicalPersonnel=VALUES(MedicalPersonnel),
                    WelfareInstitutions=VALUES(WelfareInstitutions), WelfareBeds=VALUES(WelfareBeds)
            """
            cursor.execute(sql, (
                county_code, year, to_int(row.get('医院、卫生院床位数(床)')),
                to_int(row.get('医院和卫生院卫生人员数_卫生技术人员(人)')),
                to_int(row.get('各种社会福利收养性单位数(个)')), to_int(row.get('各种社会福利收养性单位床位数(床)'))
            ))
            inserted += 1
        except Exception as e:
            print(f"导入county_healthcare表错误: {e}")
    
    conn.commit()
    print(f"county_healthcare表导入完成，共 {inserted} 条记录")
    cursor.close()


def import_poverty_counties(conn):
    """导入poverty_counties表"""
    print("导入poverty_counties表...")
    df = pd.read_csv(DATA_DIR / 'poverty_county_list.csv', dtype={'行政区划代码': str})
    cursor = conn.cursor()
    inserted = 0
    
    for _, row in df.iterrows():
        try:
            county_code_raw = row['行政区划代码']
            if pd.notna(county_code_raw):
                try:
                    county_code = str(int(float(county_code_raw))).zfill(6)
                except (ValueError, TypeError):
                    county_code = str(county_code_raw).replace('.0', '').zfill(6)
            else:
                continue
            if len(county_code) > 6:
                county_code = county_code[:6]
            
            sql = """
                INSERT INTO poverty_counties (
                    CountyCode, CountyName, Region, Province, City, ExitYear
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    CountyName=VALUES(CountyName), Region=VALUES(Region),
                    Province=VALUES(Province), City=VALUES(City), ExitYear=VALUES(ExitYear)
            """
            cursor.execute(sql, (
                county_code, clean_value(row.get('县域名称')), clean_value(row.get('所属地域')),
                clean_value(row.get('所属省份')), clean_value(row.get('所属城市')), to_int(row.get('摘帽时间'))
            ))
            inserted += 1
        except Exception as e:
            print(f"导入poverty_counties表错误: {e}")
    
    conn.commit()
    print(f"poverty_counties表导入完成，共 {inserted} 条记录")
    cursor.close()


def import_agricultural_output(conn):
    """导入agricultural_output表"""
    print("导入agricultural_output表...")
    df = pd.read_csv(DATA_DIR / 'county_agri_output.csv', dtype={'县域代码': str}, low_memory=False)
    cursor = conn.cursor()
    inserted = 0
    skipped = 0
    
    cursor.execute("SELECT CountyCode FROM county")
    valid_codes = {row[0] for row in cursor.fetchall()}
    
    for _, row in df.iterrows():
        try:
            county_code = str(row['县域代码']).zfill(6)
            if county_code not in valid_codes:
                skipped += 1
                if skipped <= 5:
                    print(f"  跳过: 县代码 {county_code} 在county表中不存在")
                continue
            
            year = to_int(row.get('统计年度'))
            product_type = clean_value(row.get('产品种类或名称'))
            if not year or not product_type:
                continue
            
            sql = """
                INSERT INTO agricultural_output (CountyCode, Year, ProductType, Unit, Output)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE Unit=VALUES(Unit), Output=VALUES(Output)
            """
            cursor.execute(sql, (
                county_code, year, product_type, clean_value(row.get('单位')), to_float64(row.get('产量'))
            ))
            inserted += 1
        except Exception as e:
            print(f"导入agricultural_output表错误: {e}")
    
    conn.commit()
    print(f"agricultural_output表导入完成，共 {inserted} 条记录" + (f"，跳过 {skipped} 条" if skipped > 0 else ""))
    cursor.close()


def import_crop_area(conn):
    """导入crop_area表"""
    print("导入crop_area表...")
    df = pd.read_csv(DATA_DIR / 'county_crop_area.csv', dtype={'县域代码': str}, low_memory=False)
    cursor = conn.cursor()
    inserted = 0
    skipped = 0
    
    cursor.execute("SELECT CountyCode FROM county")
    valid_codes = {row[0] for row in cursor.fetchall()}
    
    for _, row in df.iterrows():
        try:
            county_code = str(row['县域代码']).zfill(6)
            if county_code not in valid_codes:
                skipped += 1
                continue
            
            year = to_int(row.get('统计年度'))
            crop_type = clean_value(row.get('农作物种类或名称'))
            if not year or not crop_type:
                continue
            
            sql = """
                INSERT INTO crop_area (CountyCode, Year, CropType, SownArea)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE SownArea=VALUES(SownArea)
            """
            cursor.execute(sql, (
                county_code, year, crop_type, to_float64(row.get('播种面积-公顷'))
            ))
            inserted += 1
        except Exception as e:
            print(f"导入crop_area表错误: {e}")
    
    conn.commit()
    print(f"crop_area表导入完成，共 {inserted} 条记录" + (f"，跳过 {skipped} 条" if skipped > 0 else ""))
    cursor.close()


def import_finance_budget(conn):
    """导入finance_budget表"""
    print("导入finance_budget表...")
    df = pd.read_csv(DATA_DIR / 'county_finance_budget_raw.csv', dtype={'CountyCode': str}, low_memory=False)
    cursor = conn.cursor()
    inserted = 0
    
    for _, row in df.iterrows():
        try:
            county_code = str(row['CountyCode']).zfill(6)
            year = to_int(row.get('SgnYear'))
            project = clean_value(row.get('Project'))
            if not year or not project:
                continue
            
            sql = """
                INSERT INTO finance_budget (CountyCode, Year, Project, FinRevenue)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE FinRevenue=VALUES(FinRevenue)
            """
            cursor.execute(sql, (county_code, year, project, to_float64(row.get('FinRevenue'))))
            inserted += 1
        except Exception as e:
            print(f"导入finance_budget表错误: {e}")
    
    conn.commit()
    print(f"finance_budget表导入完成，共 {inserted} 条记录")
    cursor.close()


def import_transport_post(conn):
    """导入transport_post表"""
    print("导入transport_post表...")
    df = pd.read_csv(DATA_DIR / 'county_transport_post.csv', dtype={'CountyCode': str}, low_memory=False)
    cursor = conn.cursor()
    inserted = 0
    
    for _, row in df.iterrows():
        try:
            county_code = str(row['CountyCode']).zfill(6)
            year = to_int(row.get('SgnYear'))
            if not year:
                continue
            
            sql = """
                INSERT INTO transport_post (
                    CountyCode, Year, HighwayLength, PostBusinessVolume,
                    FixedPhoneNum, MobileUserNum
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    HighwayLength=VALUES(HighwayLength), PostBusinessVolume=VALUES(PostBusinessVolume),
                    FixedPhoneNum=VALUES(FixedPhoneNum), MobileUserNum=VALUES(MobileUserNum)
            """
            cursor.execute(sql, (
                county_code, year, to_float64(row.get('HighwayLength')),
                to_float64(row.get('PostTelBusinessVolume')), to_float64(row.get('FixedPhoneNum')),
                to_float64(row.get('MobileUserNum'))
            ))
            inserted += 1
        except Exception as e:
            print(f"导入transport_post表错误: {e}")
    
    conn.commit()
    print(f"transport_post表导入完成，共 {inserted} 条记录")
    cursor.close()


def import_financial_services(conn):
    """导入financial_services表"""
    print("导入financial_services表...")
    df = pd.read_csv(DATA_DIR / 'county_financial_services.csv', dtype={'CountyCode': str}, low_memory=False)
    cursor = conn.cursor()
    inserted = 0
    skipped = 0
    
    for _, row in df.iterrows():
        try:
            county_code = str(row['CountyCode']).zfill(6)
            year = to_int(row.get('SgnYear'))
            if not year:
                continue
            
            max_val = 9999999999.99
            loan_val = to_float64(row.get('Loan'))
            if loan_val is not None and abs(loan_val) > max_val:
                loan_val = max_val if loan_val > 0 else -max_val
            
            deposit_val = to_float64(row.get('Deposit'))
            if deposit_val is not None and abs(deposit_val) > max_val:
                deposit_val = max_val if deposit_val > 0 else -max_val
            
            savings_val = to_float64(row.get('SavingsDeposit'))
            if savings_val is not None and abs(savings_val) > max_val:
                savings_val = max_val if savings_val > 0 else -max_val
            
            sql = """
                INSERT INTO financial_services (CountyCode, Year, Loan, Deposit, SavingsDeposit)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    Loan=VALUES(Loan), Deposit=VALUES(Deposit), SavingsDeposit=VALUES(SavingsDeposit)
            """
            cursor.execute(sql, (county_code, year, loan_val, deposit_val, savings_val))
            inserted += 1
        except Exception as e:
            skipped += 1
            if skipped <= 5:
                print(f"导入financial_services表错误: {e}")
    
    conn.commit()
    print(f"financial_services表导入完成，共 {inserted} 条记录" + (f"，跳过 {skipped} 条" if skipped > 0 else ""))
    cursor.close()


def import_surveyors(conn):
    """导入surveyors表"""
    print("导入surveyors表...")
    df = pd.read_csv(DATA_DIR / 'surveyors.csv', dtype={'调研员ID': str, '负责县域ID': str})
    cursor = conn.cursor()
    inserted = 0
    
    for _, row in df.iterrows():
        try:
            surveyor_id = clean_value(row.get('调研员ID'))
            county_code = clean_value(row.get('负责县域ID'))
            if county_code:
                county_code = str(county_code).zfill(6)
            else:
                county_code = None
            
            sql = """
                INSERT INTO surveyors (
                    SurveyorID, Name, Gender, Department, Education, Major,
                    Phone, Email, TeamID, CountyCode, Role, Batch,
                    StartDate, EndDate, CompletedInterviews, PendingInterviews,
                    Expertise, TrainingStatus, EquipmentStatus, Notes
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    Name=VALUES(Name), Gender=VALUES(Gender), Department=VALUES(Department),
                    Education=VALUES(Education), Major=VALUES(Major), Phone=VALUES(Phone),
                    Email=VALUES(Email), TeamID=VALUES(TeamID), CountyCode=VALUES(CountyCode),
                    Role=VALUES(Role), Batch=VALUES(Batch), StartDate=VALUES(StartDate),
                    EndDate=VALUES(EndDate), CompletedInterviews=VALUES(CompletedInterviews),
                    PendingInterviews=VALUES(PendingInterviews), Expertise=VALUES(Expertise),
                    TrainingStatus=VALUES(TrainingStatus), EquipmentStatus=VALUES(EquipmentStatus),
                    Notes=VALUES(Notes)
            """
            cursor.execute(sql, (
                surveyor_id, clean_value(row.get('姓名')), clean_value(row.get('性别')),
                clean_value(row.get('所属院系')), clean_value(row.get('学历')), clean_value(row.get('专业方向')),
                clean_value(row.get('联系电话')), clean_value(row.get('电子邮箱')), clean_value(row.get('所属分队ID')),
                county_code, clean_value(row.get('调研角色')), clean_value(row.get('参与调研批次')),
                pd.to_datetime(row.get('调研开始时间'), errors='coerce'),
                pd.to_datetime(row.get('调研结束时间'), errors='coerce'),
                to_int(row.get('已完成访谈次数')), to_int(row.get('待补访次数')),
                clean_value(row.get('调研专长')), clean_value(row.get('培训完成状态')),
                clean_value(row.get('设备领用状态')), clean_value(row.get('备注'))
            ))
            inserted += 1
        except Exception as e:
            print(f"导入surveyors表错误: {e}")
    
    conn.commit()
    print(f"surveyors表导入完成，共 {inserted} 条记录")
    cursor.close()


def import_interviews(conn):
    """导入interviews表"""
    print("导入interviews表...")
    df = pd.read_csv(DATA_DIR / 'interviews.csv', dtype={'访谈记录id': str, '调研人id': str, '县id': str})
    cursor = conn.cursor()
    inserted = 0
    
    for _, row in df.iterrows():
        try:
            interview_id = clean_value(row.get('访谈记录id'))
            surveyor_id = clean_value(row.get('调研人id'))
            county_code = str(row.get('县id')).zfill(6)
            
            sql = """
                INSERT INTO interviews (
                    InterviewID, SurveyorID, CountyCode, IntervieweeID,
                    IntervieweeName, IntervieweeInfo, Content, InterviewDate,
                    InterviewLocation, Quality
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    SurveyorID=VALUES(SurveyorID), CountyCode=VALUES(CountyCode),
                    IntervieweeID=VALUES(IntervieweeID), IntervieweeName=VALUES(IntervieweeName),
                    IntervieweeInfo=VALUES(IntervieweeInfo), Content=VALUES(Content),
                    InterviewDate=VALUES(InterviewDate), InterviewLocation=VALUES(InterviewLocation),
                    Quality=VALUES(Quality)
            """
            cursor.execute(sql, (
                interview_id, surveyor_id, county_code, clean_value(row.get('访谈对象id')),
                clean_value(row.get('受访人姓名')), clean_value(row.get('受访人信息')),
                clean_value(row.get('访谈内容')), pd.to_datetime(row.get('访谈时间'), errors='coerce'),
                clean_value(row.get('访谈地点')), to_float64(row.get('访谈质量'))
            ))
            inserted += 1
        except Exception as e:
            print(f"导入interviews表错误: {e}")
    
    conn.commit()
    print(f"interviews表导入完成，共 {inserted} 条记录")
    cursor.close()


def main():
    """主函数"""
    print("=" * 60)
    print("832工程数据导入脚本")
    print("=" * 60)
    
    if not DATA_DIR.exists():
        print(f"错误: 数据目录不存在: {DATA_DIR}")
        sys.exit(1)
    
    try:
        conn = get_db_connection()
        print("数据库连接成功\n")
    except Exception as e:
        print(f"数据库连接失败: {e}")
        print("请检查数据库配置和连接信息")
        sys.exit(1)
    
    try:
        import_county_table(conn)
        import_county_nature(conn)
        import_poverty_counties(conn)
        import_county_economy(conn)
        import_county_agriculture(conn)
        import_county_population(conn)
        import_county_healthcare(conn)
        import_agricultural_output(conn)
        import_crop_area(conn)
        import_finance_budget(conn)
        import_transport_post(conn)
        import_financial_services(conn)
        import_surveyors(conn)
        import_interviews(conn)
        
        print("\n" + "=" * 60)
        print("所有数据导入完成！")
        print("=" * 60)
    except Exception as e:
        print(f"\n导入过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()
        print("数据库连接已关闭")


if __name__ == '__main__':
    main()


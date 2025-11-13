# 832工程数据库ER图设计

## 实体关系图概述

本数据库系统围绕832个原国家级贫困县的脱贫攻坚数据，设计包含12个核心实体表，支持县域经济、自然地理、调研访谈等多维度数据管理。

## 核心实体

### 1. 县行政区划表 (county)
**主键**: CountyCode (6位数字行政区划代码)
**属性**:
- CountyCode: 县域行政区划代码 (主键)
- CountyName: 地区名称
- Province: 所属省份
- City: 所属城市
- Longitude: 经度
- Latitude: 纬度
- LandArea: 行政区域土地面积(平方公里)
- TownshipCount: 乡及镇个数
- VillageCount: 乡个数

### 2. 县自然表 (county_nature)
**主键**: CountyCode
**外键**: CountyCode → county(CountyCode)
**属性**:
- CountyCode: 县域代码 (主键, 外键)
- RegionLevel: 地区等级
- TerrainRelief: 地形起伏度
- Longitude: 经度
- Latitude: 纬度

### 3. 县经济表 (county_economy)
**主键**: (CountyCode, Year)
**外键**: CountyCode → county(CountyCode)
**属性**:
- CountyCode: 县域代码 (外键)
- Year: 年份
- GDP: 地区生产总值(万元)
- GDP_Primary: 第一产业增加值(万元)
- GDP_Secondary: 第二产业增加值(万元)
- GDP_Tertiary: 第三产业增加值(万元)
- PerCapitaGDP: 人均地区生产总值(元/人)
- UrbanAvgWage: 城镇单位在岗职工平均工资(元)
- RuralDisposableIncome: 农村居民人均可支配收入(元)
- FiscalRevenue: 地方财政一般预算收入(万元)
- FiscalExpenditure: 地方财政一般预算支出(万元)
- SavingsDeposit: 城乡居民储蓄存款余额(万元)
- LoanBalance: 年末金融机构各项贷款余额(万元)
- IndustrialOutput: 规模以上工业总产值(万元)
- IndustrialEnterpriseCount: 规模以上工业企业数(个)
- FixedAssetInvestment: 全社会固定资产投资(万元)
- RetailSales: 社会消费品零售总额(万元)

### 4. 县农业表 (county_agriculture)
**主键**: (CountyCode, Year)
**外键**: CountyCode → county(CountyCode)
**属性**:
- CountyCode: 县域代码 (外键)
- Year: 年份
- CropArea: 农作物总播种面积(千公顷)
- MachineryPower: 农业机械总动力(万千瓦特)
- GrainOutput: 粮食总产量(吨)
- CottonOutput: 棉花产量(吨)
- OilOutput: 油料产量(吨)
- MeatOutput: 肉类总产量(吨)
- AgriOutputValue: 农林牧渔业总产值(万元)
- RuralLaborForce: 乡村从业人员数(人)
- AgriLaborForce: 农林牧渔业从业人员数(人)

### 5. 县人口表 (county_population)
**主键**: (CountyCode, Year)
**外键**: CountyCode → county(CountyCode)
**属性**:
- CountyCode: 县域代码 (外键)
- Year: 年份
- RegisteredPopulation: 户籍人口数(万人)
- PrimarySchoolTeachers: 普通小学专任教师数(人)
- MiddleSchoolTeachers: 普通中学专任教师数(人)
- PrimarySchoolStudents: 普通小学在校生数(人)
- MiddleSchoolStudents: 普通中学在校学生数(人)

### 6. 县医疗表 (county_healthcare)
**主键**: (CountyCode, Year)
**外键**: CountyCode → county(CountyCode)
**属性**:
- CountyCode: 县域代码 (外键)
- Year: 年份
- HospitalBeds: 医院、卫生院床位数(床)
- MedicalPersonnel: 医院和卫生院卫生人员数_卫生技术人员(人)
- WelfareInstitutions: 各种社会福利收养性单位数(个)
- WelfareBeds: 各种社会福利收养性单位床位数(床)

### 7. 贫困县列表 (poverty_counties)
**主键**: CountyCode
**外键**: CountyCode → county(CountyCode)
**属性**:
- CountyCode: 县域代码 (主键, 外键)
- CountyName: 县域名称
- Region: 所属地域 (东部/中部/西部)
- Province: 所属省份
- City: 所属城市
- ExitYear: 摘帽时间

### 8. 农业产出明细表 (agricultural_output)
**主键**: (CountyCode, Year, ProductType)
**外键**: CountyCode → county(CountyCode)
**属性**:
- CountyCode: 县域代码 (外键)
- Year: 统计年度
- ProductType: 产品种类或名称
- Unit: 单位
- Output: 产量

### 9. 农作物面积表 (crop_area)
**主键**: (CountyCode, Year, CropType)
**外键**: CountyCode → county(CountyCode)
**属性**:
- CountyCode: 县域代码 (外键)
- Year: 统计年度
- CropType: 农作物种类或名称
- SownArea: 播种面积(公顷)

### 10. 财政预算表 (finance_budget)
**主键**: (CountyCode, Year, Project)
**外键**: CountyCode → county(CountyCode)
**属性**:
- CountyCode: 县域代码 (外键)
- Year: 年份
- Project: 项目名称
- FinRevenue: 财政收入(万元)

### 11. 交通邮政表 (transport_post)
**主键**: (CountyCode, Year)
**外键**: CountyCode → county(CountyCode)
**属性**:
- CountyCode: 县域代码 (外键)
- Year: 年份
- HighwayLength: 公路长度(公里)
- PostBusinessVolume: 邮政业务量(万元)
- FixedPhoneNum: 固定电话用户数(万户)
- MobileUserNum: 移动用户数(万户)

### 12. 金融服务表 (financial_services)
**主键**: (CountyCode, Year)
**外键**: CountyCode → county(CountyCode)
**属性**:
- CountyCode: 县域代码 (外键)
- Year: 年份
- Loan: 贷款余额(亿元)
- Deposit: 存款余额(亿元)
- SavingsDeposit: 储蓄存款余额(亿元)

### 13. 调研员表 (surveyors)
**主键**: SurveyorID
**外键**: CountyCode → county(CountyCode)
**属性**:
- SurveyorID: 调研员ID (主键)
- Name: 姓名
- Gender: 性别
- Department: 所属院系
- Education: 学历
- Major: 专业方向
- Phone: 联系电话
- Email: 电子邮箱
- TeamID: 所属分队ID
- CountyCode: 负责县域ID (外键)
- Role: 调研角色
- Batch: 参与调研批次
- StartDate: 调研开始时间
- EndDate: 调研结束时间
- CompletedInterviews: 已完成访谈次数
- PendingInterviews: 待补访次数
- Expertise: 调研专长
- TrainingStatus: 培训完成状态
- EquipmentStatus: 设备领用状态
- Notes: 备注

### 14. 访谈内容表 (interviews)
**主键**: InterviewID
**外键**: 
- SurveyorID → surveyors(SurveyorID)
- CountyCode → county(CountyCode)
**属性**:
- InterviewID: 访谈记录id (主键)
- SurveyorID: 调研人id (外键)
- CountyCode: 县id (外键)
- IntervieweeID: 访谈对象id
- IntervieweeName: 受访人姓名
- IntervieweeInfo: 受访人信息
- Content: 访谈内容
- InterviewDate: 访谈时间
- InterviewLocation: 访谈地点
- Quality: 访谈质量评分

## 实体关系

1. **county** (1) ←→ (N) **county_economy**: 一个县有多年的经济数据
2. **county** (1) ←→ (1) **county_nature**: 一个县对应一条自然地理数据
3. **county** (1) ←→ (N) **county_agriculture**: 一个县有多年的农业数据
4. **county** (1) ←→ (N) **county_population**: 一个县有多年的人口数据
5. **county** (1) ←→ (N) **county_healthcare**: 一个县有多年的医疗数据
6. **county** (1) ←→ (0..1) **poverty_counties**: 一个县可能是贫困县（一对一或零对一）
7. **county** (1) ←→ (N) **agricultural_output**: 一个县有多种农业产出
8. **county** (1) ←→ (N) **crop_area**: 一个县有多种农作物面积
9. **county** (1) ←→ (N) **finance_budget**: 一个县有多项财政预算
10. **county** (1) ←→ (N) **transport_post**: 一个县有多年的交通邮政数据
11. **county** (1) ←→ (N) **financial_services**: 一个县有多年的金融服务数据
12. **county** (1) ←→ (N) **surveyors**: 一个县可以有多个调研员
13. **surveyors** (1) ←→ (N) **interviews**: 一个调研员可以进行多次访谈
14. **county** (1) ←→ (N) **interviews**: 一个县可以有多次访谈记录

## 规范化说明

- **第一范式(1NF)**: 所有表都满足原子性，每个字段不可再分
- **第二范式(2NF)**: 所有表都消除了部分函数依赖，时间序列表使用复合主键(CountyCode, Year)
- **第三范式(3NF)**: 消除了传递依赖，县的基本信息集中在county表，避免冗余

## 设计原则

1. **主键设计**: 使用CountyCode作为核心外键，确保数据一致性
2. **时间序列**: 经济、农业、人口等时间序列数据使用(CountyCode, Year)复合主键
3. **数据分离**: 将不同主题的数据分离到不同表，便于维护和查询
4. **外键约束**: 建立完整的外键关系，保证数据完整性
5. **索引优化**: 在CountyCode和Year字段上建立索引，提高查询性能


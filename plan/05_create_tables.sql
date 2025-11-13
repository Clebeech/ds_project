-- 832工程数据库建表脚本
-- 数据库名称: poverty_alleviation_832
-- 字符集: utf8mb4
-- 排序规则: utf8mb4_unicode_ci

-- 创建数据库
CREATE DATABASE IF NOT EXISTS poverty_alleviation_832 
    DEFAULT CHARACTER SET utf8mb4 
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE poverty_alleviation_832;

-- 1. 县行政区划表（核心主表）
CREATE TABLE county (
    CountyCode CHAR(6) PRIMARY KEY COMMENT '县域行政区划代码',
    CountyName VARCHAR(100) NOT NULL COMMENT '地区名称',
    Province VARCHAR(50) NOT NULL COMMENT '所属省份',
    City VARCHAR(50) NOT NULL COMMENT '所属城市',
    Longitude DECIMAL(10, 6) COMMENT '经度',
    Latitude DECIMAL(10, 6) COMMENT '纬度',
    LandArea DECIMAL(12, 2) COMMENT '行政区域土地面积(平方公里)',
    TownshipCount INT COMMENT '乡及镇个数',
    VillageCount INT COMMENT '乡个数',
    INDEX idx_province (Province),
    INDEX idx_city (City)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='县行政区划表';

-- 2. 县自然表
CREATE TABLE county_nature (
    CountyCode CHAR(6) PRIMARY KEY COMMENT '县域代码',
    RegionLevel TINYINT COMMENT '地区等级',
    TerrainRelief DECIMAL(8, 6) COMMENT '地形起伏度',
    Longitude DECIMAL(10, 6) COMMENT '经度',
    Latitude DECIMAL(10, 6) COMMENT '纬度',
    FOREIGN KEY (CountyCode) REFERENCES county(CountyCode) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='县自然表';

-- 3. 县经济表
CREATE TABLE county_economy (
    CountyCode CHAR(6) NOT NULL COMMENT '县域代码',
    Year INT NOT NULL COMMENT '年份',
    GDP DECIMAL(15, 2) COMMENT '地区生产总值(万元)',
    GDP_Primary DECIMAL(15, 2) COMMENT '第一产业增加值(万元)',
    GDP_Secondary DECIMAL(15, 2) COMMENT '第二产业增加值(万元)',
    GDP_Tertiary DECIMAL(15, 2) COMMENT '第三产业增加值(万元)',
    PerCapitaGDP DECIMAL(10, 2) COMMENT '人均地区生产总值(元/人)',
    UrbanAvgWage DECIMAL(10, 2) COMMENT '城镇单位在岗职工平均工资(元)',
    RuralDisposableIncome DECIMAL(10, 2) COMMENT '农村居民人均可支配收入(元)',
    FiscalRevenue DECIMAL(15, 2) COMMENT '地方财政一般预算收入(万元)',
    FiscalExpenditure DECIMAL(15, 2) COMMENT '地方财政一般预算支出(万元)',
    SavingsDeposit DECIMAL(15, 2) COMMENT '城乡居民储蓄存款余额(万元)',
    LoanBalance DECIMAL(15, 2) COMMENT '年末金融机构各项贷款余额(万元)',
    IndustrialOutput DECIMAL(15, 2) COMMENT '规模以上工业总产值(万元)',
    IndustrialEnterpriseCount INT COMMENT '规模以上工业企业数(个)',
    FixedAssetInvestment DECIMAL(15, 2) COMMENT '全社会固定资产投资(万元)',
    RetailSales DECIMAL(15, 2) COMMENT '社会消费品零售总额(万元)',
    PRIMARY KEY (CountyCode, Year),
    FOREIGN KEY (CountyCode) REFERENCES county(CountyCode) ON DELETE CASCADE,
    INDEX idx_year (Year)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='县经济表';

-- 4. 县农业表
CREATE TABLE county_agriculture (
    CountyCode CHAR(6) NOT NULL COMMENT '县域代码',
    Year INT NOT NULL COMMENT '年份',
    CropArea DECIMAL(10, 2) COMMENT '农作物总播种面积(千公顷)',
    MachineryPower DECIMAL(10, 2) COMMENT '农业机械总动力(万千瓦特)',
    GrainOutput DECIMAL(12, 2) COMMENT '粮食总产量(吨)',
    CottonOutput DECIMAL(10, 2) COMMENT '棉花产量(吨)',
    OilOutput DECIMAL(10, 2) COMMENT '油料产量(吨)',
    MeatOutput DECIMAL(10, 2) COMMENT '肉类总产量(吨)',
    AgriOutputValue DECIMAL(15, 2) COMMENT '农林牧渔业总产值(万元)',
    RuralLaborForce INT COMMENT '乡村从业人员数(人)',
    AgriLaborForce INT COMMENT '农林牧渔业从业人员数(人)',
    PRIMARY KEY (CountyCode, Year),
    FOREIGN KEY (CountyCode) REFERENCES county(CountyCode) ON DELETE CASCADE,
    INDEX idx_year (Year)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='县农业表';

-- 5. 县人口表
CREATE TABLE county_population (
    CountyCode CHAR(6) NOT NULL COMMENT '县域代码',
    Year INT NOT NULL COMMENT '年份',
    RegisteredPopulation DECIMAL(8, 2) COMMENT '户籍人口数(万人)',
    PrimarySchoolTeachers INT COMMENT '普通小学专任教师数(人)',
    MiddleSchoolTeachers INT COMMENT '普通中学专任教师数(人)',
    PrimarySchoolStudents INT COMMENT '普通小学在校生数(人)',
    MiddleSchoolStudents INT COMMENT '普通中学在校学生数(人)',
    PRIMARY KEY (CountyCode, Year),
    FOREIGN KEY (CountyCode) REFERENCES county(CountyCode) ON DELETE CASCADE,
    INDEX idx_year (Year)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='县人口表';

-- 6. 县医疗表
CREATE TABLE county_healthcare (
    CountyCode CHAR(6) NOT NULL COMMENT '县域代码',
    Year INT NOT NULL COMMENT '年份',
    HospitalBeds INT COMMENT '医院、卫生院床位数(床)',
    MedicalPersonnel INT COMMENT '医院和卫生院卫生人员数_卫生技术人员(人)',
    WelfareInstitutions INT COMMENT '各种社会福利收养性单位数(个)',
    WelfareBeds INT COMMENT '各种社会福利收养性单位床位数(床)',
    PRIMARY KEY (CountyCode, Year),
    FOREIGN KEY (CountyCode) REFERENCES county(CountyCode) ON DELETE CASCADE,
    INDEX idx_year (Year)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='县医疗表';

-- 7. 贫困县列表
CREATE TABLE poverty_counties (
    CountyCode CHAR(6) PRIMARY KEY COMMENT '县域代码',
    CountyName VARCHAR(100) NOT NULL COMMENT '县域名称',
    Region VARCHAR(20) COMMENT '所属地域',
    Province VARCHAR(50) NOT NULL COMMENT '所属省份',
    City VARCHAR(50) NOT NULL COMMENT '所属城市',
    ExitYear INT COMMENT '摘帽时间',
    FOREIGN KEY (CountyCode) REFERENCES county(CountyCode) ON DELETE CASCADE,
    INDEX idx_region (Region),
    INDEX idx_exit_year (ExitYear)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='贫困县列表';

-- 8. 农业产出明细表
CREATE TABLE agricultural_output (
    CountyCode CHAR(6) NOT NULL COMMENT '县域代码',
    Year INT NOT NULL COMMENT '统计年度',
    ProductType VARCHAR(100) NOT NULL COMMENT '产品种类或名称',
    Unit VARCHAR(20) COMMENT '单位',
    Output DECIMAL(15, 2) COMMENT '产量',
    PRIMARY KEY (CountyCode, Year, ProductType),
    FOREIGN KEY (CountyCode) REFERENCES county(CountyCode) ON DELETE CASCADE,
    INDEX idx_year (Year),
    INDEX idx_product (ProductType)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='农业产出明细表';

-- 9. 农作物面积表
CREATE TABLE crop_area (
    CountyCode CHAR(6) NOT NULL COMMENT '县域代码',
    Year INT NOT NULL COMMENT '统计年度',
    CropType VARCHAR(100) NOT NULL COMMENT '农作物种类或名称',
    SownArea DECIMAL(12, 2) COMMENT '播种面积(公顷)',
    PRIMARY KEY (CountyCode, Year, CropType),
    FOREIGN KEY (CountyCode) REFERENCES county(CountyCode) ON DELETE CASCADE,
    INDEX idx_year (Year),
    INDEX idx_crop (CropType)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='农作物面积表';

-- 10. 财政预算表
CREATE TABLE finance_budget (
    CountyCode CHAR(6) NOT NULL COMMENT '县域代码',
    Year INT NOT NULL COMMENT '年份',
    Project VARCHAR(200) NOT NULL COMMENT '项目名称',
    FinRevenue DECIMAL(15, 2) COMMENT '财政收入(万元)',
    PRIMARY KEY (CountyCode, Year, Project),
    FOREIGN KEY (CountyCode) REFERENCES county(CountyCode) ON DELETE CASCADE,
    INDEX idx_year (Year),
    INDEX idx_project (Project)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='财政预算表';

-- 11. 交通邮政表
CREATE TABLE transport_post (
    CountyCode CHAR(6) NOT NULL COMMENT '县域代码',
    Year INT NOT NULL COMMENT '年份',
    HighwayLength DECIMAL(10, 2) COMMENT '公路长度(公里)',
    PostBusinessVolume DECIMAL(10, 2) COMMENT '邮政业务量(万元)',
    FixedPhoneNum DECIMAL(8, 2) COMMENT '固定电话用户数(万户)',
    MobileUserNum DECIMAL(8, 2) COMMENT '移动用户数(万户)',
    PRIMARY KEY (CountyCode, Year),
    FOREIGN KEY (CountyCode) REFERENCES county(CountyCode) ON DELETE CASCADE,
    INDEX idx_year (Year)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='交通邮政表';

-- 12. 金融服务表
CREATE TABLE financial_services (
    CountyCode CHAR(6) NOT NULL COMMENT '县域代码',
    Year INT NOT NULL COMMENT '年份',
    Loan DECIMAL(12, 2) COMMENT '贷款余额(亿元)',
    Deposit DECIMAL(12, 2) COMMENT '存款余额(亿元)',
    SavingsDeposit DECIMAL(12, 2) COMMENT '储蓄存款余额(亿元)',
    PRIMARY KEY (CountyCode, Year),
    FOREIGN KEY (CountyCode) REFERENCES county(CountyCode) ON DELETE CASCADE,
    INDEX idx_year (Year)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='金融服务表';

-- 13. 调研员表
CREATE TABLE surveyors (
    SurveyorID VARCHAR(20) PRIMARY KEY COMMENT '调研员ID',
    Name VARCHAR(50) NOT NULL COMMENT '姓名',
    Gender CHAR(1) COMMENT '性别',
    Department VARCHAR(100) COMMENT '所属院系',
    Education VARCHAR(20) COMMENT '学历',
    Major VARCHAR(100) COMMENT '专业方向',
    Phone VARCHAR(20) COMMENT '联系电话',
    Email VARCHAR(100) COMMENT '电子邮箱',
    TeamID VARCHAR(20) COMMENT '所属分队ID',
    CountyCode CHAR(6) COMMENT '负责县域ID',
    Role VARCHAR(50) COMMENT '调研角色',
    Batch VARCHAR(50) COMMENT '参与调研批次',
    StartDate DATE COMMENT '调研开始时间',
    EndDate DATE COMMENT '调研结束时间',
    CompletedInterviews INT DEFAULT 0 COMMENT '已完成访谈次数',
    PendingInterviews INT DEFAULT 0 COMMENT '待补访次数',
    Expertise VARCHAR(200) COMMENT '调研专长',
    TrainingStatus VARCHAR(10) COMMENT '培训完成状态',
    EquipmentStatus VARCHAR(10) COMMENT '设备领用状态',
    Notes TEXT COMMENT '备注',
    FOREIGN KEY (CountyCode) REFERENCES county(CountyCode) ON DELETE SET NULL,
    INDEX idx_team (TeamID),
    INDEX idx_county (CountyCode)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='调研员表';

-- 14. 访谈内容表
CREATE TABLE interviews (
    InterviewID VARCHAR(20) PRIMARY KEY COMMENT '访谈记录id',
    SurveyorID VARCHAR(20) NOT NULL COMMENT '调研人id',
    CountyCode CHAR(6) NOT NULL COMMENT '县id',
    IntervieweeID VARCHAR(50) COMMENT '访谈对象id',
    IntervieweeName VARCHAR(100) COMMENT '受访人姓名',
    IntervieweeInfo TEXT COMMENT '受访人信息',
    Content TEXT COMMENT '访谈内容',
    InterviewDate DATE COMMENT '访谈时间',
    InterviewLocation VARCHAR(200) COMMENT '访谈地点',
    Quality DECIMAL(3, 1) COMMENT '访谈质量评分',
    FOREIGN KEY (SurveyorID) REFERENCES surveyors(SurveyorID) ON DELETE CASCADE,
    FOREIGN KEY (CountyCode) REFERENCES county(CountyCode) ON DELETE CASCADE,
    INDEX idx_surveyor (SurveyorID),
    INDEX idx_county (CountyCode),
    INDEX idx_date (InterviewDate)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='访谈内容表';


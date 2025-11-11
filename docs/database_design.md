# 832 数据库系统数据模型草案

## 1. 设计摘要
- 支撑角色：政策分析师、调研员、系统管理员。
- 核心实体：县域（行政区划）、年度县域指标（经济/自然/金融）、调研员、访谈记录。
- 主数据键：全部以国家统计局 6 位县级行政区划代码 `county_code` 作为跨表主键；时间维采用公历年份 `stat_year`。
- 范围：依据 `data/` 目录内现有 Excel；`data/archive/全国832个国家贫困县历年摘帽名单.xlsx` 为文本公告，暂不入库。

## 2. 实体与字段

### 2.1 `county`
| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `county_code` | CHAR(6) PK | 县级行政区划代码 |
| `county_name` | VARCHAR(64) | 县/区名称 |
| `prefecture_name` | VARCHAR(64) | 地级市/盟 |
| `province_name` | VARCHAR(64) | 省级行政区 |
| `area_id` | VARCHAR(16) | 数据源 `AreaID`（若存在） |
| `region_tag` | VARCHAR(16) | 东/中/西部（来源贫困县名单，可选） |
| `is_target_county` | BOOLEAN | 是否在 832 工程范围 |

来源：`data/各县基本数据/*.xlsx`、`data/archive/全国832个国家级贫困县名单.xlsx`、`data/对应县.xlsx`。

### 2.2 `county_profile`
`data/各县基本数据/综合数据.xlsx`

- 主键：(`county_code`, `stat_year`)
- 包含行政面积、人口、农业、产业、教育、医疗等 40+ 指标（全部转换 `FLOAT8`，NULL 表示缺失）。
- 建议字段示例：
  - `land_area_sqkm`, `township_count`, `registered_pop`, `agri_workforce`, `gdp_total`, `gdp_primary`, `gdp_secondary`, `gdp_tertiary`, `gdp_per_capita`, `avg_wage`, `rural_income`, `fiscal_revenue`, `fiscal_expenditure`, `savings_balance`, `loan_balance`, `crop_area`, `grain_output`, `meat_output`, `agri_output`, `industry_enterprise_count`, `industry_output`, `fixed_asset_investment`, `retail_sales`, `primary_teacher_count`, `primary_student_count`, `hospital_bed_count`, `welfare_bed_count` 等。

### 2.3 专题年度指标表
| 表名 | 来源 | 主键 | 主要字段 |
| --- | --- | --- | --- |
| `county_population` | `人口.xlsx` | (`county_code`,`stat_year`) | `population_total` |
| `county_gdp` | `地区生产总值及指数.xlsx` | 同上 | `gdp_total`, `gdp_primary` …, `gdp_per_capita`（与综合表重复，可用于核对） |
| `county_income` | `城乡居民收入.xlsx` | 同上 | `urban_disposable_income`, `rural_net_income`, `rural_disposable_income` |
| `county_transport_post` | `交通运输与邮电.xlsx` | 同上 | `highway_length`, `post_telecom_volume`, `fixed_phone_users`, `mobile_users` |
| `county_finance_budget` | `财政收支.xlsx` | (`county_code`,`stat_year`,`project_code`) | `project_name`, `amount`，`project_code` 由 `Identify` 或自建枚举 |
| `county_financial_services` | `金融机构存贷款.xlsx` | (`county_code`,`stat_year`) | `loan_balance`, `deposit_balance`, `savings_balance` |
| `county_agri_output` | `archive/中国各县域农产品产量数据.xlsx` | (`county_code`,`stat_year`,`product_code`) | `product_name`, `unit`, `output_value` |
| `county_crop_area` | `archive/中国各县域农作物播种面积数据.xlsx` | (`county_code`,`stat_year`,`crop_code`) | `crop_name`, `sown_area_ha` |
| `county_relief_topography` | `archive/中国各县域地形起伏度数据.xlsx` | `county_code` | `relief_amplitude`, `longitude`, `latitude` |
| `county_precipitation_monthly` | `archive/中国各县域逐月平均降水量统计.xlsx` | (`county_code`,`stat_month`) | `precip_mm`（需将宽表转长表；数据跨度大，可按需裁剪年份） |

### 2.4 `survey_team`
| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `team_id` | VARCHAR(16) PK | `所属分队ID` |
| `team_name` | VARCHAR(64) | 可选（无则留空） |
| `cohort` | VARCHAR(32) | 批次信息，如“2021年夏季批次” |

### 2.5 `surveyor`
| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `surveyor_id` | VARCHAR(16) PK | 形如 `DY2021****` |
| `full_name` | VARCHAR(32) |
| `gender` | VARCHAR(8) |
| `school` | VARCHAR(64) | 所属院系 |
| `education_level` | VARCHAR(16) |
| `major` | VARCHAR(64) |
| `phone` | VARCHAR(32) |
| `email` | VARCHAR(64) |
| `team_id` | VARCHAR(16) FK → `survey_team` |
| `primary_county_code` | CHAR(6) FK → `county` |
| `role` | VARCHAR(32) |
| `batch_label` | VARCHAR(32) |
| `start_date` | DATE | Excel 序列号需转 `DATE` |
| `end_date` | DATE |
| `interview_completed` | INTEGER |
| `interview_pending` | INTEGER |
| `expertise` | TEXT |
| `training_completed` | BOOLEAN |
| `equipment_status` | VARCHAR(32) |
| `notes` | TEXT |

### 2.6 `interview`
| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `interview_id` | VARCHAR(16) PK | `访谈记录id` |
| `surveyor_id` | VARCHAR(16) FK → `surveyor` |
| `county_code` | CHAR(6) FK → `county` |
| `interviewee_id` | VARCHAR(32) | `访谈对象id` |
| `interviewee_name` | VARCHAR(32) |
| `interviewee_profile` | TEXT |
| `transcript` | TEXT | 合并后的访谈内容；需清理 `\\xa0` 等不可见字符 |
| `interview_date` | DATE | 由 Excel 序列号转 |
| `location` | VARCHAR(128) |
| `quality_score` | INTEGER |
| `created_at` | TIMESTAMP DEFAULT NOW() |

### 2.7 `county_case_mapping`
| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `county_code` | CHAR(6) PK/FK | 对应 `负责县域ID` |
| `county_alias` | VARCHAR(64) | `对应县` |
| `region_detail` | VARCHAR(64) | `地区` |
| `note` | TEXT |

用于承接 `data/对应县.xlsx` 与主 `county` 表之间的别名或备注。

## 3. 关系与约束
- `county` ↔ 各年度指标表：一对多；所有从表均需 `FOREIGN KEY (county_code)`。
- `survey_team` ↔ `surveyor`：一对多。
- `surveyor` ↔ `interview`：一对多。
- `county` ↔ `interview`：一对多（支持一条访谈关联一个县域）。
- `county` ↔ `county_case_mapping`：一对一/可选，用于记录县域别名或驻点信息。
- 对于多项目指标（如财政收支、农产品产量），建议增加维表：
  - `dim_finance_project(project_code, project_name, category)`
  - `dim_agri_product(product_code, product_name, unit)`
  - `dim_crop(crop_code, crop_name)`

## 4. 索引建议
- `county_profile`、`county_population` 等年度表：复合索引 `idx_{table}_county_year (county_code, stat_year)`.
- 多项目表：`idx_{table}_county_year_code (county_code, stat_year, *_code)`.
- `interview`：`idx_interview_county_date (county_code, interview_date)`，`idx_interview_surveyor (surveyor_id)`.
- `surveyor`：唯一索引 `uq_surveyor_phone`、`uq_surveyor_email`（视数据完整性决定）。

## 5. 数据治理与清洗要点
1. **编码统一**：所有 Excel 导入前先转换为 `float64`/`string`，清理 `\\xa0`、全角空格。
2. **日期处理**：Excel 序列号（如 44378、45092）批量转 `DATE`；无法解析的保持 `NULL`。
3. **单位标准化**：明确万元/千公顷/吨等单位，写入数据字典；必要时换算后存储。
4. **缺失值**：保留 `NULL`，避免使用 0 代替，保证统计准确。
5. **重复值检查**：导入前按 (`county_code`,`stat_year`) 去重；出现冲突记录需人工确认。
6. **降水数据**：由于时间跨度大，可按业务需要截取 2000 年后数据或按季聚合，避免宽表照搬。

## 6. ER 模型文字描述
- `county` 为中心节点，与所有年度指标表建立一对多关系。
- `surveyor` 通过外键依赖 `survey_team` 与 `county`（负责县域），其访谈成果保存在 `interview` 中，与 `county` 形成案例关系。
- 专题指标（财政、农业、降水等）可视为事实表，配套维表管理项目、产品、作物等维度。

## 7. 后续文档
- 根据本草案补充字段详细定义与单位，形成正式数据字典。
- 依据上述结构绘制 ER 图（PowerDesigner、draw.io 等）。
- 在数据装载阶段记录 ETL 脚本与异常处理日志。



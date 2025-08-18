from mignonFramework import InsertQuick, Logger, ConfigManager, inject, QueueIter, target, Rename, extractDDL2List
from mignonFramework.utils import SqlDDL2List


log = Logger(True)
config = ConfigManager("./resources/config/insertConfig.ini")

queueStarter = QueueIter(config)


@inject(config)
class RowsData:
    rows: int
    num: int


rowsData = config.getInstance(RowsData)


def insertCallback(status: bool, data_batch: list[dict], filename: str, line_num: int):
    if status and line_num > 0:
        rowsData.rows = line_num

    if not status:
        raise Exception("插入失败")


def moditerFunc(dic: dict) -> dict:
    return {
        "ipcTypeCN": Rename("ipcTypeCN")
    }

strs = """
       -- auto-generated definition
       create table patent_info_hzh
       (
           title                   varchar(2048)                       null comment '专利标题',
           abstract_ab             text                                null comment '摘要',
           application_num         varchar(100)                        null comment '申请号',
           publication_number      varchar(100)                        null comment '公开（公告）号',
           publication_date        date                                null comment '公开（公告）日',
           application_date        date                                null comment '申请日',
           patent_type_cn_stat     varchar(50)                         null comment '专利类型 (中文统计)',
           patent_status           varchar(50)                         null comment '专利状态',
           applicants              json                                null comment '申请人列表',
           applicant_addr          varchar(2048)                       null comment '申请人地址',
           assignees               json                                null comment '专利权人（受让人）列表',
           assignees_addr          varchar(2048)                       null comment '专利权人（受让人）地址',
           inventors               json                                null comment '发明人列表',
           last_legal_status       varchar(50)                         null comment '最新法律状态',
           legal_date              date                                null comment '法律状态公告日',
           expired_date            date                                null comment '失效日',
           patent_duration         varchar(50)                         null comment '专利保护期',
           ipc_main                text                                null comment '主要IPC分类号',
           ipcTypeCN               text                                null comment 'IPC分类号对应的中文含义',
           ipc_mainclass_num       int                                 null comment 'IPC主分类号数量',
           application_country     varchar(200)                        null comment '申请国家',
           publication_country     varchar(200)                        null comment '公开国家',
           province_name           varchar(150)                        null comment '省份名称',
           city_name               varchar(50)                         null comment '城市名称',
           district_name           varchar(150)                        null comment '区/县名称',
           claims                  longtext                            null comment '权利要求书 (HTML格式)',
           description             longtext                            null comment '说明书 (HTML格式)',
           datasource_stat         varchar(50)                         null comment '数据来源地',
           kind_code               varchar(10)                         null comment '文献类型代码',
           data_type               varchar(20)                         null comment '数据类型',
           application_num_sear    varchar(100)                        null comment '用于检索的申请号',
           publication_number_sear varchar(100)                        null comment '用于检索的公开号'
       )
           comment '海知汇专利信息表';

       create index idx_type_and_id
           on patent_info_hzh (patent_type_cn_stat, id);

       create index idx_type_asc_id_desc
           on patent_info_hzh (patent_type_cn_stat, id); \
       """



InsertQuick(
   eazy=True
).run("D:\专利\备份\科技成果.txt", rowsData.rows)

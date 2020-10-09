import pymysql
from PapersCrawler import settings

class PapersDB:
    def __init__(self):
        # 打开数据库连接
        self.db = pymysql.connect(settings.DB_HOST, settings.DB_USER, settings.DB_PW, settings.DB_DBN)
        self.db.set_charset("utf8")
        self.cursor = self.db.cursor()
        self.cursor.execute('SET NAMES utf8;')
        self.cursor.execute('SET CHARACTER SET utf8;')
        self.cursor.execute('SET character_set_connection=utf8;')

    def insert_paper(self, paper_row):
        # 使用cursor()方法获取操作游标
        cursor = self.cursor

        # # 重复不插入
        # sql_check = "select * from papers WHERE `title` = '%s' AND `authors` = '%s'" % (pymysql.escape_string(paper_row["title"]), pymysql.escape_string(paper_row["authors"]))
        # cursor.execute(sql_check)
        # if cursor.fetchone() is not None: return False, "重复..."

        # SQL 插入语句
        sql = "INSERT INTO papers(`title`, \
                                        `authors`, `category`, `year`, `publish_in`, `conf_journal`, `cj_name`, `level`, `cat`) \
                                        VALUES ('%s', '%s', '%s', '%d', '%s', '%s', '%s', '%s', '%s')" % \
              (pymysql.escape_string(paper_row["title"]), pymysql.escape_string(paper_row["authors"]), pymysql.escape_string(paper_row["category"]),
               int(paper_row["year"]), pymysql.escape_string(paper_row["publish_in"]), paper_row["conf_journal"], paper_row["name"], paper_row["level"], paper_row["cat"])

        try:
            # 执行sql语句
            row = cursor.execute(sql)
            # 执行sql语句
            self.db.commit()
            if row == 1: return True, "成功插入"
        except Exception as e:
            # 发生错误时回滚
            self.db.rollback()
            print(paper_row)
            print("insert error! e:")
            print(e)
            return False, "%s \n %s" % (paper_row, e)

    def close(self):
        self.cursor.close()
        self.db.close()
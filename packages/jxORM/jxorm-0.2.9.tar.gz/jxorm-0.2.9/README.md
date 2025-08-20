
jxORM是配套jxWebUI使用的数据库操作库。

### 版本更新说明

0.1.1版本的修改：

1、不允许数据对象修改主键

### 使用说明

jxORM的使用非常简单，主要包括几个步骤：

1、导入依赖

	from jxORM import jxORMLogger, ORM, DBDataType, ColType, jxDB

2、设置数据库连接
    
    #用默认设置，设置本地的mysql数据库连接
	jxDB.set('testDB', password='password')

目前，jxORM支持mysql和sqlite两种数据库。

3、定义一个类，然后用ORM进行修饰，以表明其是一个jxORM数据类

    @ORM
	class User:
        ID:DBDataType.Long = ColType.PrimaryKey
        CreateTime:DBDataType.DataTime = 1
        Nameame:DBDataType.Chars = 2
        Type:DBDataType.Chars = 2
        Info:DBDataType.Json

上述代码定义了一个数据类也是同名的数据表【User】，其属性如下：

| 名称         | 类型       | 说明          |
|------------|----------|-------------|
| ID         | Long     | 主键          |
| CreateTime | DataTime | 索引1         |
| Name       | 字符串      | 联合索引2       |
| Type       | 字符串      | 联合索引2       |
| Info       | json     | json格式的附属数据 |

4、在数据库中创建数据表

在操作数据前需要先获得数据库连接对象：db。在jxWebUI中，每个事件响应函数在调用时会自动获取到db，我们可以直接使用：

	User.create(db)

这条语句会在数据库中创建一个名为【user】的表，其建表语句如下：

    CREATE TABLE `User` (
    `ID` bigint NOT NULL,
    `CreateTime` datetime NOT NULL,
    `Name` varchar(126) NOT NULL,
    `Type` varchar(126) NOT NULL,
    `Info` mediumtext NOT NULL,
    PRIMARY KEY (`ID`),
    KEY `User_index_1` (`CreateTime`),
    KEY `User_index_2` (`Name`,`Type`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

如果数据库中已经存在名为【User】的表，那么会在日志中记录表已经存在，但不会影响后继的执行。

5、插入数据

    user = User()
    user.Name = 'admin'
    user.Type = 'admin'
    user.Info = {'name': 'admin', 'pwd': '123456'}
    user.insert(db)

则会在表User中插入一条记录。ID、CreateTime会自动生成。

6、修改数据

    user.Name = 'test'
    user.Type = 'normal'
    user.update(db)

7、查询数据

    u = User.Get(db, 'Name == "admin"‘)

如果只执行了5而未执行6，则返回前面创建的admin用户。如果已经执行了6，则返回None。

查询数据有多种方式以适应不同的查询需求，具体请参考【查询数据】。

<font color=red size=3>注：</font>jxORM不支持删除，一般通过设置一个bool型属性来实现逻辑删除

### 扩展数据

经常会遇到新需求需要扩展原有的数据表。jxORM提供了非常简便的扩展数据的方法：继承性扩展：
    
    @ORM
    class User2(User):
        ID:DBDataType.Long = ColType.PrimaryKey
        State:DBDataType.Chars = 1
        Noused:DBDataType.Bool
    User2.create(db)

这就创建了一个新的数据表和数据类：User2。对于数据类User2来说，其具有User类的所有属性，同时还具有新的属性：State和Noused。

    u = User2()
    u.Name = 'test2'
    u.Type = 'xxxxxxxxx'
    u.State = 'ok'
    u.Info = {'a':1, 'b':2}
    u.insert(db)

而User2数据表的建表语句如下：

    CREATE TABLE `User2` (
      `ID` bigint NOT NULL,
      `State` varchar(126) NOT NULL,
      `Noused` tinyint NOT NULL,
      PRIMARY KEY (`ID`),
      KEY `User2_index_1` (`State`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci

其只有User2类的定义。所以，上述u.insert(db)是将数据分别插入到User和User2表中。jxORM会自动完成相应的处理。

同理，update和相关的**类数据查询方法**也会自动完成具有继承关系的数据类所对应的数据表之间的关联。

<font color=red size=3>注：</font>具有继承关系的数据表必须定义Long型的ID属性为主键，而且所有子类也都必须如此，否则jxORM无法完成关联。

这种方式的最大好处是在扩展数据后，原本使用User的老代码，不受任何影响【如，原本修改User表新增字段的方式，如果新增字段定义为NOT NULL，老代码插入数据时就会因无法插入而崩溃】。新的代码则使用User2即可。

使用了User2的新代码，在查询时由于jxORM会自动关联User和User2表，而老代码只使用了User表，所以老代码插入的数据，新代码无法查询的到。同理，其它通过继承创建了User3、User4的代码也会和User2形成隔离。

### 日志

引用jxORM后，会在当前目录下的logs子目录【没有则会自动创建】中会创建一个日志文件：

- jxORM.log：是jxORM的运行日志，会记录所有的数据库操作等

日志都是30个日志文件、每个日志文件500M进行循环，所以如长期运行需注意硬盘空间的使用情况。

### 安装jxORM

	pip install jxORM

### 接入jxWebUI

按下述代码即可将jxORM接入到jxWebUI中：

    from jxWebUI import jxWebSQLGetDBConnection
    from jxORM import get_default_db
    
    jxWebSQLGetDBConnection(get_default_db, is_custom=True)

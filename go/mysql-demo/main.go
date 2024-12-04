package main

import (
	"database/sql"
	"fmt"
	"strconv"

	"github.com/gin-gonic/gin"
	_ "github.com/go-sql-driver/mysql"
)

func shenhezhong(db *sql.DB, c *gin.Context) {
	// 假设你要更新表中的某个字段
	updateStmt := `update hcs_config set ` + "`value`" + `  = 'true' where config_code = 'WXMINI_AUDIT_SWITCH' limit 1;`
	fmt.Printf(updateStmt)
	// 执行 UPDATE 操作
	result, err := db.Exec(updateStmt)
	if err != nil {
		fmt.Println("更新失败:", err)
		return
	}

	// 获取影响的行数
	rowsAffected, err := result.RowsAffected()
	if err != nil {
		fmt.Println("获取影响行数失败:", err)
		return
	}

	msg := "成功更新了" + strconv.FormatInt(rowsAffected, 10) + "行"
	c.String(200, msg)
}

func shenhetongguo(db *sql.DB, c *gin.Context) {
	// 假设你要更新表中的某个字段
	updateStmt := `update hcs_config set ` + "`value`" + `  = 'false' where config_code = 'WXMINI_AUDIT_SWITCH' limit 1;`
	fmt.Printf(updateStmt)
	// 执行 UPDATE 操作
	result, err := db.Exec(updateStmt)
	if err != nil {
		fmt.Println("更新失败:", err)
		return
	}

	// 获取影响的行数
	rowsAffected, err := result.RowsAffected()
	if err != nil {
		fmt.Println("获取影响行数失败:", err)
		return
	}

	msg := "成功更新了" + strconv.FormatInt(rowsAffected, 10) + "行"
	c.String(200, msg)
}

// 数据库连接配置
const (
	DBHost     = "127.0.0.1"
	DBPort     = 3306
	DBUser     = "health"
	DBPassword = "123456"
	DBName     = "dev_1"
)

func main() {
	// Create a new Gin router
	r := gin.Default()

	// DSN (Data Source Name) 是包含数据库连接信息的字符串
	dsn := fmt.Sprintf("%s:%s@tcp(%s:%d)/%s?charset=utf8mb4", DBUser, DBPassword, DBHost, DBPort, DBName)

	// 创建数据库连接
	db, err := sql.Open("mysql", dsn)
	if err != nil {
		panic(err.Error())
	}
	defer db.Close()

	// 检查连接是否有效
	err = db.Ping()
	if err != nil {
		panic(err.Error())
	} else {
		fmt.Println("Connected to the database!！！！！！！")
	}

	var maxOpenConns = 10
	var maxIdleConns = 5
	db.SetMaxOpenConns(maxOpenConns)
	db.SetMaxIdleConns(maxIdleConns)

	// Define a route that responds with "Hello, World!" when accessed
	r.GET("/shenhezhong", func(c *gin.Context) {
		fmt.Println("执行审核中SQL")
		shenhezhong(db, c)

	})
	r.GET("/shenhetongguo", func(c *gin.Context) {
		fmt.Println("执行审核通过SQL")
		shenhetongguo(db, c)
	})

	// Start the server on port 8080
	r.Run(":8080")
}


package config

import "github.com/spf13/viper"

var AppConfig struct {
	AppHost              string
	AppPort              int
	DBMongoHost          string
	DBMongoPort          int
	DBMongoDB            string
	SearchOptionOrderBy  string
	SearchOptionOrder    string
	SearchOptionPageSize int
}

// InitConfig 用于加载配置文件和解析配置参数
func InitConfig() error {
	// 初始化 viper
	viper.SetConfigName("config") // 指定配置文件的名称（config.json）
	viper.AddConfigPath(".")      // 指定配置文件的路径（当前目录）

	// 读取配置文件
	if err := viper.ReadInConfig(); err != nil {
		return err
	}

	// 从配置文件中获取配置参数并存储到 AppConfig 中
	AppConfig.AppHost = viper.GetString("app.host")
	AppConfig.AppPort = viper.GetInt("app.port")
	AppConfig.DBMongoHost = viper.GetString("database.mongodb.host")
	AppConfig.DBMongoPort = viper.GetInt("database.mongodb.port")
	AppConfig.DBMongoDB = viper.GetString("database.mongodb.db")
	AppConfig.SearchOptionOrderBy = viper.GetString("searchOption.OrderBy")
	AppConfig.SearchOptionOrder = viper.GetString("searchOption.Order")
	AppConfig.SearchOptionPageSize = viper.GetInt("searchOption.pageSize")

	return nil
}

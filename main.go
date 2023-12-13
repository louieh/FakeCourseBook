package main

import (
	"fmt"
	"log"
	"net/http"
	"reflect"
	"strconv"
	"time"

	cache "github.com/chenyahui/gin-cache"
	"github.com/chenyahui/gin-cache/persist"
	"github.com/gin-gonic/gin"
	"github.com/louieh/FakeCourseBook/config"
	"github.com/louieh/FakeCourseBook/middleware"
	"github.com/louieh/FakeCourseBook/models"
	"github.com/louieh/FakeCourseBook/models/params"
	"github.com/louieh/FakeCourseBook/utils"
	"github.com/louieh/FakeCourseBook/utils/loginUtils"
	"github.com/louieh/FakeCourseBook/utils/mongoUtils"

	docs "github.com/louieh/FakeCourseBook/docs"
	swaggerfiles "github.com/swaggo/files"
	ginSwagger "github.com/swaggo/gin-swagger"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo/options"
)

func StructToBSONM(data interface{}) (bson.M, error) {
	document, err := bson.Marshal(data)
	if err != nil {
		return nil, err
	}

	var result bson.M
	err = bson.Unmarshal(document, &result)
	if err != nil {
		return nil, err
	}

	return result, nil
}

// StructToBSONMWithTags 将结构体转换为 bson.M，使用结构体字段的 JSON 标签作为键
func StructToBSONMWithTags(data interface{}) (bson.M, error) {
	// 使用反射获取结构体字段的 JSON 标签
	value := reflect.ValueOf(data)
	if value.Kind() != reflect.Struct {
		return nil, fmt.Errorf("Input is not a struct")
	}

	document := bson.M{}
	typ := reflect.TypeOf(data)

	for i := 0; i < value.NumField(); i++ {
		field := value.Field(i)
		key := typ.Field(i).Tag.Get("json") // 获取字段的 JSON 标签

		if key == "" {
			key = typ.Field(i).Name // 如果没有 JSON 标签，使用字段名称作为键
		}

		// 将字段值添加到 bson.M
		document[key] = field.Interface()
	}

	return document, nil
}

func setSearchOptions(filter params.SearchOptions, bsonMFilter *bson.M) {
	defaults := map[string]interface{}{
		"class_term":   "",
		"class_status": "",
		"class_day":    "",
		"class_title":  "",
	}

	v := reflect.ValueOf(filter)
	t := reflect.TypeOf(filter)

	for i := 0; i < v.NumField(); i++ {
		field := v.Field(i)
		key := t.Field(i).Tag.Get("json")
		defaultValue := defaults[key]

		if key != "" && field.Interface() != defaultValue {
			(*bsonMFilter)[key] = field.Interface()
		}
	}
}

// @BasePath /api/v1

// search godoc
// @Summary search
// @Schemes
// @Description do search
// @Tags search
// @Accept json
// @Produce json
// @Success 200 {string} Search
// @Router /search [POST]
// @Param	pageNumber	query	int	false	"page number"	default(1)
// @Param	pageSize	query	int	false	"page size" defualt(10)
// @Param 	orderBy		query	string  false	"order feild" defualt(class_title)
// @Param	order		query	string  false	"order" Enums(des, asc)
// @Param 	class_term body string false "message/rfc822"
// @Param 	class_status body string false "message/rfc822"
// @Param 	class_prefix body string false "message/rfc822"
func search(c *gin.Context) {
	// get query
	pageNumber := c.DefaultQuery("pageNumber", "1")
	pageNumberInt, err := strconv.Atoi(pageNumber)
	if err != nil {
		log.Fatal(err)
	}
	pageSizeInt := config.AppConfig.SearchOptionPageSize
	pageSize := c.Query("pageSize")
	if pageSize != "" {
		pageSizeInt, err = strconv.Atoi(pageSize)
		if err != nil {
			log.Fatal(err)
		}
	}
	skip := (pageNumberInt - 1) * pageSizeInt
	sortBy := c.DefaultQuery("orderBy", config.AppConfig.SearchOptionOrderBy)
	order := c.DefaultQuery("order", config.AppConfig.SearchOptionOrder)
	// set default sort
	orderInt := 1
	if order == "des" {
		orderInt = -1
	}
	sort := bson.D{{sortBy, orderInt}}

	// get params and set filter
	filter := params.SearchOptions{}
	if err := c.ShouldBindJSON(&filter); err != nil {
		log.Fatal(err)
	}
	fmt.Println("filter: ", filter)
	bsonMFilter := bson.M{}
	setSearchOptions(filter, &bsonMFilter)
	fmt.Println("bsonMFilter: ", bsonMFilter)

	// search
	options := options.Find().
		SetSkip(int64(skip)).
		SetLimit(int64(pageSizeInt)).
		SetSort(sort)
	// container
	var res []models.CourseForSearch
	mongoUtils.DoFind(c, config.AppConfig.DBMongoCollectionSearch, bsonMFilter, options, &res)
	c.JSON(http.StatusOK, res)
}

// @BasePath /api/v1

// list all professor godoc
// @Summary list all professor
// @Schemes
// @Description list all professor
// @Tags search
// @Accept json
// @Produce json
// @Success 200 {string} Search
// @Router /listProfessors [GET]
func listProfessors(c *gin.Context) {
	// option
	projection := bson.M{"class_instructor": 1, "_id": 0}
	options := options.Find().
		SetProjection(projection)
	// container
	var res []models.ProfessorsList
	mongoUtils.DoFind(c, config.AppConfig.DBMongoCollectionSearch, bson.M{}, options, &res)
	c.JSON(http.StatusOK, res)
}

// @BasePath /api/v1

// list all course godoc
// @Summary list all course
// @Schemes
// @Description list all course
// @Tags search
// @Accept json
// @Produce json
// @Success 200 {string} Search
// @Router /listCourses [GET]
func listCourses(c *gin.Context) {
	// option
	projection := bson.M{"class_section": 1,
		"class_number": 1,
		"class_title":  1,
		"_id":          0}
	options := options.Find().SetProjection(projection)
	// container
	var res []models.CoursesList
	mongoUtils.DoFind(c, config.AppConfig.DBMongoCollectionSearch, bson.M{}, options, &res)
	c.JSON(http.StatusOK, res)
}

// @BasePath /api/v1

// fetch professor rate godoc
// @Summary fetch professor rate
// @Schemes
// @Description fetch professor rate
// @Tags search
// @Accept json
// @Produce json
// @Success 200 {string} Search
// @Router /fetchProRate/{name} [GET]
func fetchProfessorRate(c *gin.Context) {
	name := c.Param("name")
	c.JSON(http.StatusOK, utils.FetchRateMyProfessor(name))
}

// @BasePath /api/v1

// fetch course description godoc
// @Summary fetch course description
// @Schemes
// @Description fetch course description
// @Tags search
// @Accept json
// @Produce json
// @Success 200 {string} Search
// @Router /fetchCourDisc/{sectionNumber} [GET]
func fetchCourseDiscreption(c *gin.Context) {
	sectionNum := c.Param("secNum")
	c.JSON(http.StatusOK, utils.FetchCourseDiscreption(sectionNum))
}

func fetchCoursePage(c *gin.Context) {
	// courseSection := c.Param("secNum")
	// res1 := utils.GetCourseGraphData(courseSection, true)
	req, _ := c.Get("request")
	fmt.Println("-----------request:", req)
	param := params.GetSpeedGraphDataParam{ClassNumber: "24043"}
	res2 := utils.GetSpeedGraphData(param)
	c.JSON(http.StatusOK, res2)
}

func fetchProfessorPage(c *gin.Context) {}

func loginOAuth(c *gin.Context) {
	authCode := c.Query("code")
	fmt.Println("-=-=-=0=-0 code: ", authCode)
	username, jwt := loginUtils.OAuthGithub(c, authCode)
	c.JSON(http.StatusOK, map[string]string{"username": username, "jwt": jwt})
}

func main() {
	// 初始化配置
	if err := config.InitConfig(); err != nil {
		log.Fatalf("初始化配置失败: %v", err)
	}
	router := gin.Default()
	memoryStore := persist.NewMemoryStore(1 * time.Minute)
	router.Use(middleware.CommonMiddleWare())
	// api/v1
	apiV1 := router.Group("api/v1")

	apiV1.Use(middleware.LoginCheck())
	{
		apiV1.POST("/search", search)
		apiV1.GET("/listProfessors", listProfessors)
		apiV1.GET("/listCourses", listCourses)
		apiV1.GET("/fetchProRate/:name", fetchProfessorRate)
		apiV1.GET("/fetchCourDisc/:secNum", fetchCourseDiscreption)
		apiV1.GET("/fetchCoursePage/:secNum", cache.CacheByRequestURI(memoryStore, 2*time.Second), fetchCoursePage)
		apiV1.GET("/fetchProfessorPage/:name", fetchProfessorPage)
	}

	// login api
	router.GET("/login/oauth", loginOAuth)

	docs.SwaggerInfo.BasePath = "/api/v1"
	router.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerfiles.Handler))
	router.Run(fmt.Sprintf("%s:%d", config.AppConfig.AppHost, config.AppConfig.AppPort))
}

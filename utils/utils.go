package utils

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"slices"
	"strings"

	"github.com/antchfx/htmlquery"
	"github.com/louieh/FakeCourseBook/config"
	"github.com/louieh/FakeCourseBook/models"
	"github.com/louieh/FakeCourseBook/utils/mongoUtils"
	"go.mongodb.org/mongo-driver/bson"
	"go.mongodb.org/mongo-driver/mongo/options"
)

func FetchCourseDiscreption(sectionNum string) string {
	url := "https://catalog.utdallas.edu/2023/graduate/courses/" + sectionNum
	respBody := downloador(url, "GET", nil, nil)
	doc, err := htmlquery.Parse(respBody)
	if err != nil {
		panic(err)
	}

	// 使用XPath查询
	node := htmlquery.FindOne(doc, ".//div[@id='bukku-page']/p")

	// 输出链接
	return htmlquery.InnerText(node)
}

func FetchRateMyProfessor(name string) map[string]any {
	url := "https://www.ratemyprofessors.com/graphql"
	data := map[string]any{
		"query": "query TeacherSearchResultsPageQuery(\n  $query: TeacherSearchQuery!\n  $schoolID: ID\n) {\n  search: newSearch {\n    ...TeacherSearchPagination_search_1ZLmLD\n  }\n  school: node(id: $schoolID) {\n    __typename\n    ... on School {\n      name\n    }\n    id\n  }\n}\n\nfragment TeacherSearchPagination_search_1ZLmLD on newSearch {\n  teachers(query: $query, first: 8, after: \"\") {\n    didFallback\n    edges {\n      cursor\n      node {\n        ...TeacherCard_teacher\n        id\n        __typename\n      }\n    }\n    pageInfo {\n      hasNextPage\n      endCursor\n    }\n    resultCount\n    filters {\n      field\n      options {\n        value\n        id\n      }\n    }\n  }\n}\n\nfragment TeacherCard_teacher on Teacher {\n  id\n  legacyId\n  avgRating\n  numRatings\n  ...CardFeedback_teacher\n  ...CardSchool_teacher\n  ...CardName_teacher\n  ...TeacherBookmark_teacher\n}\n\nfragment CardFeedback_teacher on Teacher {\n  wouldTakeAgainPercent\n  avgDifficulty\n}\n\nfragment CardSchool_teacher on Teacher {\n  department\n  school {\n    name\n    id\n  }\n}\n\nfragment CardName_teacher on Teacher {\n  firstName\n  lastName\n}\n\nfragment TeacherBookmark_teacher on Teacher {\n  id\n  isSaved\n}\n",
		"variables": map[string]any{
			"query": map[string]any{
				"text":         name,
				"schoolID":     "",
				"fallback":     true,
				"departmentID": nil,
			},
			"schoolID": "",
		},
	}

	respBody := downloador(url, "POST", map[string]string{"Authorization": "Basic dGVzdDp0ZXN0"}, data)
	defer respBody.Close()
	// printResp(respBody)
	var result map[string]interface{}
	decoder := json.NewDecoder(respBody)
	err := decoder.Decode(&result)
	if err != nil {
		panic(err)
	}
	return result
}

func downloador(url string, method string, header map[string]string, data any) io.ReadCloser {
	// 创建包含 JSON 数据的请求体
	jsonData, err := json.Marshal(data)
	if err != nil {
		panic(err)
	}
	requestBody := bytes.NewBuffer(jsonData)

	request, err := http.NewRequest(method, url, requestBody)
	if err != nil {
		panic(err)
	}
	// 设置请求头
	for k, v := range header {
		request.Header.Set(k, v)
	}
	// 发送请求
	client := http.Client{}
	response, err := client.Do(request)
	if err != nil {
		panic(err)
	}
	// 检查响应状态
	if response.StatusCode != http.StatusOK {
		fmt.Println("Error: ", response.Status)
		panic(response.StatusCode)
	}
	return response.Body
}

func printResp(respBody io.ReadCloser) {
	// 读取响应体
	body, err := io.ReadAll(respBody)
	if err != nil {
		panic(err)
	}

	// 使用 json.Indent 将 JSON 数据格式化
	var prettyJSON bytes.Buffer
	err = json.Indent(&prettyJSON, body, "", "  ")
	if err != nil {
		panic(err)
	}

	// 打印格式化后的 JSON 数据
	fmt.Println("----------------resp: ", prettyJSON.String())
}

type tempProNameStruct struct {
	Name  string `json:"name"`
	Value string `json:"value"`
}

func GetCourseGraphData(courseSection string, _6301_7301 bool) map[string]any {
	// filter
	bsonMFilter := bson.M{}
	if !_6301_7301 {
		bsonMFilter["class_section"] = bson.M{"$regex": courseSection}
	} else {
		bsonMFilter["class_title"] = bson.M{"$regex": courseSection}
	}
	// option
	projection := bson.M{"_id": 0}
	options := options.Find().
		SetProjection(projection)
	var allCourseList []models.CourseForGrade
	mongoUtils.DoFind(context.Background(), config.AppConfig.DBMongoCollectionGrade, bsonMFilter, options, &allCourseList)

	if len(allCourseList) == 0 {
		log.Fatal("allCourseList is empty")
		// TODO abort 404
	}

	courseName := allCourseList[0].ClassTitle
	var courseSectionRes string
	if !_6301_7301 {
		courseSectionRes = strings.ReplaceAll(strings.ToLower(courseSection), " ", "")
	} else {
		courseSectionRes = strings.ReplaceAll(strings.ToLower(strings.Split(allCourseList[0].ClassSection, ".")[0]), " ", "")
	}

	var professorList []string
	termDict := make(map[string][]tempProNameStruct)

	for _, courseStruct := range allCourseList {
		professorNameList := courseStruct.ClassInstructor
		professorList = append(professorList, professorNameList...)
		term := courseStruct.ClassTerm
		for _, eachProName := range professorNameList {
			tempProNameDict := tempProNameStruct{eachProName, eachProName}
			if !slices.Contains(termDict[term], tempProNameDict) {
				termDict[term] = append(termDict[term], tempProNameDict)
			}
		}
	}

	var finalList []map[string]any
	for _, term := range config.AppConfig.TermList {
		tempFinalDict := map[string]any{"name": term, "children": termDict[term]}
		finalList = append(finalList, tempFinalDict)
	}
	finalDict := map[string]any{"name": courseSection, "children": finalList}

	return map[string]any{"courseSectionRes": courseSectionRes, "courseName": courseName, "finalDict": finalDict, "professorNameList": professorList}
}

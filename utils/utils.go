package utils

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"

	"github.com/antchfx/htmlquery"
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

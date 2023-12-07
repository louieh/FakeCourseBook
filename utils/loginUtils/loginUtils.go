package loginUtils

import (
	"encoding/json"
	"fmt"

	"github.com/gin-gonic/gin"
	"github.com/louieh/FakeCourseBook/config"
	"github.com/louieh/FakeCourseBook/models"
	"github.com/louieh/FakeCourseBook/utils"
	"github.com/louieh/FakeCourseBook/utils/jwtUtils"
)

func fetchGithubUserInfo(token string) models.OAuthGithubUser {
	header := map[string]string{"Authorization": "Bearer " + token, "accept": "application/json"}
	resp := utils.DoRequest(config.AppConfig.OAuthGithubUserUrl, "GET", header, nil)
	var userStruct models.OAuthGithubUser
	json.NewDecoder(resp).Decode(&userStruct)
	return userStruct
}

func OAuthGithub(c *gin.Context, code string) (string, string) {
	url := config.AppConfig.OAuthGithubTokenUrl + "?client_id=" + config.AppConfig.OAuthGithubId + "&client_secret=" + config.AppConfig.OAuthGithubSecret + "&code=" + code
	header := map[string]string{"accept": "application/json"}
	resp := utils.DoRequest(url, "POST", header, nil)
	var tokenStruct models.OAuthGithubToken
	json.NewDecoder(resp).Decode(&tokenStruct)
	fmt.Println("0-=-0=0-=0-=-0= tokenStruct: ", tokenStruct)
	userStruct := fetchGithubUserInfo(tokenStruct.AccessToken)
	fmt.Println("=--0=0-=0-==-0 userStruct: ", userStruct)
	jwt := jwtUtils.GeneratorOAuthToken(tokenStruct.AccessToken)
	// TODO create a user if it doesn't exist
	loginUser := models.LoginUserInfo{Username: userStruct.Login}
	c.Set("loginUser", loginUser)
	return userStruct.Login, jwt
}

package middleware

import (
	"fmt"
	"net/http"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/louieh/FakeCourseBook/config"
	"github.com/louieh/FakeCourseBook/utils/jwtUtils"
)

func CommonMiddleWare() gin.HandlerFunc {
	return func(c *gin.Context) {
		t := time.Now()
		fmt.Println("--------------CommonMiddleWare started")
		// c.Set("request", "CommonMiddleWare")
		c.Next()
		status := c.Writer.Status()
		fmt.Println("------------CommonMiddleWare end", status)
		t2 := time.Since(t)
		fmt.Println("------------CommonMiddleWare time:", t2)
	}
}

func LoginCheck() gin.HandlerFunc {
	return func(c *gin.Context) {
		token := c.Request.Header.Get(config.AppConfig.OAuthHeader)
		if token != "" && strings.HasPrefix(token, config.AppConfig.OAuthTokenPrefix) {
			token = strings.ReplaceAll(token, config.AppConfig.OAuthTokenPrefix, "")
		}
		fmt.Println("------------- Login Check middleware ----------token: ", token)
		claims, err := jwtUtils.ParserToken(token)
		if err != nil {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized"})
			c.Abort()
			return
		}
		fmt.Println("------------Login Check middleware claims: ", claims)
		// c.Next() api func will be called here
		status := c.Writer.Status()
		fmt.Println("------------Login Check middleware end", status)
		// otherwise api func will be called here
	}
}

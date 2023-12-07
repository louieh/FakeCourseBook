package jwtUtils

import (
	"errors"
	"fmt"
	"log"
	"time"

	"github.com/golang-jwt/jwt/v5"
	"github.com/louieh/FakeCourseBook/config"
	"github.com/louieh/FakeCourseBook/models"
)

// https://pkg.go.dev/github.com/golang-jwt/jwt/v5
// https://golang-jwt.github.io/jwt/usage/create/

func GeneratorOAuthToken(token string) string {
	claims := models.MyJwtClaims{
		OAuth:      true,
		OAuthWeb:   "github",
		OAuthToken: token,
		RegisteredClaims: jwt.RegisteredClaims{
			// A usual scenario is to set the expiration time relative to the current time
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(time.Duration(config.AppConfig.TokenExpire) * time.Hour)),
		},
	}
	res := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	ss, err := res.SignedString(config.AppConfig.AppSecretKey)
	if err != nil {
		log.Fatal(err)
	}
	return ss
}

func GeneratorToken(username string, password string) string {
	claims := models.MyJwtClaims{
		Username: username,
		Password: password,
		OAuth:    false,
		RegisteredClaims: jwt.RegisteredClaims{
			// A usual scenario is to set the expiration time relative to the current time
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(time.Duration(config.AppConfig.TokenExpire) * time.Hour)),
		},
	}
	res := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	ss, err := res.SignedString([]byte(config.AppConfig.AppSecretKey))
	if err != nil {
		log.Fatal(err)
	}
	return ss
}

func ParserToken(signedToken string) (models.MyJwtClaims, error) {
	parsedToken, err := jwt.ParseWithClaims(signedToken, &models.MyJwtClaims{}, func(token *jwt.Token) (interface{}, error) {
		return config.AppConfig.AppSecretKey, nil
	})

	if err != nil {
		fmt.Println("Error parsing token:", err)
		return models.MyJwtClaims{}, err
	}

	// get claims detail
	claims, ok := parsedToken.Claims.(*models.MyJwtClaims)
	if !ok || !parsedToken.Valid || time.Now().After(claims.ExpiresAt.Time) {
		return models.MyJwtClaims{}, errors.New("Invalid token")
	} else {
		return *claims, nil
	}
}

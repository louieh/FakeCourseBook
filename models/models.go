package models

import "github.com/golang-jwt/jwt/v5"

type Album struct {
	ID     string  `json:"id"`
	Title  string  `json:"title"`
	Artist string  `json:"artist"`
	Price  float64 `json:"price"`
}

type CourseForSearch struct {
	ClassTerm       string   `bson:"class_term"`
	ClassStatus     string   `bson:"class_status"`
	ClassPrefix     string   `bson:"class_prefix"`
	ClassSection    string   `bson:"class_section"`
	ClassMethod     string   `bson:"class_method"`
	ClassNumber     string   `bson:"class_number"`
	ClassTitle      string   `bson:"class_title"`
	ClassInstructor []string `bson:"class_instructor"`
	ClassDay        string   `bson:"class_day"`
	ClassTime       string   `bson:"class_time"`
	ClassStartTime  string   `bson:"class_start_time"`
	ClassEndTime    string   `bson:"class_end_time"`
	ClassLocation   string   `bson:"class_location"`
	ClassIsFull     string   `bson:"class_isFull"`
}

type CourseForGrade struct {
	ClassTerm       string   `bson:"class_term"`
	ClassSection    string   `bson:"class_section"`
	ClassNumber     string   `bson:"class_number"`
	ClassTitle      string   `bson:"class_title"`
	ClassInstructor []string `bson:"class_instructor"`
}

type SpeedUpdateData struct {
	Percentage float64 `bson:"percentage"`
	Timestamp  int64   `bson:"timestamp"`
}

type CourseForSpeed struct {
	ClassTerm       string            `bson:"class_term"`
	ClassSection    string            `bson:"class_section"`
	ClassNumber     string            `bson:"class_number"`
	ClassTitle      string            `bson:"class_title"`
	ClassInstructor []string          `bson:"class_instructor"`
	ClassDay        string            `bson:"class_day"`
	ClassStartTime  string            `bson:"class_start_time"`
	UpdateData      []SpeedUpdateData `bson:"update_data"`
}

type CoursesList struct {
	ClassSection string `bson:"class_section"`
	ClassNumber  string `bson:"class_number"`
	ClassTitle   string `bson:"class_title"`
}

type ProfessorsList struct {
	ClassInstructor []string `bson:"class_instructor"`
}

type OAuthGithubToken struct {
	AccessToken string `json:"access_token"`
	TokenType   string `json:"token_type"`
	Scope       string `json:"scope"`
}

type OAuthGithubUser struct {
	Login             string `json:"login"`
	Id                int    `json:"id"`
	NodeId            string `json:"node_id"`
	AvatarUrl         string `json:"avatar_url"`
	GravatarId        string `json:"gravatar_id"`
	Url               string `json:"url"`
	HtmlUrl           string `json:"html_url"`
	FollowersUrl      string `json:"followers_url"`
	FollowingUrl      string `json:"following_url"`
	GistsUrl          string `json:"gists_url"`
	StarredUrl        string `json:"starred_url"`
	SubscriptionsUrl  string `json:"subscriptions_url"`
	OrganizationsUrl  string `json:"organizations_url"`
	ReposUrl          string `json:"repos_url"`
	ReceivedEventsUrl string `json:"received_events_url"`
	Type              string `json:"type"`
	SiteAdmin         bool   `json:"site_admin"`
	Name              string `json:"name"`
	Company           string `json:"company"`
	Blog              string `json:"blog"`
	Location          string `json:"location"`
	Email             string `json:"email"`
	Hireable          bool   `json:"hireable"`
	Bio               string `json:"bio"`
	TwitterUsername   string `json:"twitter_username"`
	PublicRepos       int    `json:"public_repos"`
	PublicGists       int    `json:"public_gists"`
	Followers         int    `json:"followers"`
	Following         int    `json:"following"`
	CreatedAt         string `json:"created_at"`
	UpdatedAt         string `json:"updated_at"`
}

type MyJwtClaims struct {
	Username   string `json:"username"`
	Password   string `json:"password"`
	OAuth      bool   `json:"oauth"`
	OAuthWeb   string `json:"oauth_web"`
	OAuthToken string `json:"oauth_token"`
	jwt.RegisteredClaims
}

type LoginUserInfo struct {
	Username string `json:"username"`
	UserId   string `json:"userid"`
	Name     string `json:"name"`
}

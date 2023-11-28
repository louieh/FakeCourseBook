package models

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

type CoursesList struct {
	ClassSection string `bson:"class_section"`
	ClassNumber  string `bson:"class_number"`
	ClassTitle   string `bson:"class_title"`
}

type ProfessorsList struct {
	ClassInstructor []string `bson:"class_instructor"`
}

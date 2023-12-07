package params

type SearchOptions struct {
	ClassTerm   string `json:"class_term" binding:"omitempty"`
	ClassStatus string `json:"class_status" binding:"omitempty"`
	ClassDay    string `json:"class_day" binding:"omitempty"`
	ClassTitle  string `json:"class_title" binding:"omitempty"`
}

type GetSpeedGraphDataParam struct {
	ClassNumber     string `json:"class_number"`
	ClassTitle      string `json:"class_title"`
	ClassTerm       string `json:"class_term"`
	ClassInstructor string `json:"class_instructor"`
	ClassSection    string `json:"class_section"`
}

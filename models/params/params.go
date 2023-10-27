package params

type SearchOptions struct {
	ClassTerm   string `json:"class_term" binding:"omitempty"`
	ClassStatus string `json:"class_status" binding:"omitempty"`
	ClassDay    string `json:"class_day" binding:"omitempty"`
	ClassTitle  string `json:"class_title" binding:"omitempty"`
}

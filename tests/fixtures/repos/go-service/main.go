package main

import "net/http"

// Serve starts the example listener on the configured port.
func main() {
	http.ListenAndServe(":8080", nil)
}

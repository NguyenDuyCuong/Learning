package main

import (
	"fmt"

	"go-learning/greetings"
)

func main() {
	message := greetings.SayHello("Cuong")
	fmt.Println(message)
}

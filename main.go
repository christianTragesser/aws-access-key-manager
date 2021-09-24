package main

import (
	"github.com/christiantragesser/aws-access-key-manager/utils"
)

func main() {
	utils.SendSlackNotification("Test Message", "This is a test", "good")
}

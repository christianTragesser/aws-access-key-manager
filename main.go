package main

import (
	"os"
	"strings"

	"github.com/christiantragesser/aws-access-key-manager/utils"
	"github.com/sirupsen/logrus"
)

// var warnDays, _ = os.LookupEnv("WARN_DAYS")
var warnDays int = 85
var expireDays int = 90
var userWhiteList string = ""
var updateUserList []string = strings.Split(userWhiteList, ",")

func main() {
	slackURL, slackURL_exist := os.LookupEnv("SLACK_URL")
	if !slackURL_exist {
		logrus.Warn("Slack URL not set.")
	} else {
		logrus.Infof("Slack URL is %v", slackURL)
	}

	utils.ExamineKeys()
}

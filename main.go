package main

import (
	"os"

	"github.com/christiantragesser/aws-access-key-manager/utils"
	"github.com/sirupsen/logrus"
)

func main() {
	slackURL, slackURL_exist := os.LookupEnv("SLACK_URL")
	if !slackURL_exist {
		logrus.Warn("Slack URL not set.")
	} else {
		logrus.Infof("Slack URL is %v", slackURL)
	}

	utils.ExamineKeys()
}

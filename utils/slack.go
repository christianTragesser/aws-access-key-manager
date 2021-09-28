package utils

import (
	"bytes"
	"encoding/json"
	"io/ioutil"
	"net/http"
	"os"

	"github.com/sirupsen/logrus"
)

type slackMessageFields struct {
	Title    string `json:"title"`
	Value    string `json:"value"`
	Short    bool   `json:"short"`
	Markdown bool   `json:"mrkdwn"`
}

type slackMessage struct {
	Fallback string               `json:"fallback"`
	Color    string               `json:"color"`
	Fields   []slackMessageFields `json:"fields"`
}

type slackWebhookPayload struct {
	Username    string         `json:"username"`
	Channel     string         `json:"channel"`
	IconEmoji   string         `json:"icon_emoji"`
	Attachments []slackMessage `json:"attachments"`
}

func slackClient(webhookURL string, payload []byte) {
	response, err := http.Post(webhookURL, "application/json", bytes.NewBuffer(payload))
	if err != nil {
		logrus.Fatal(err)
	}
	defer response.Body.Close()

	body, err := ioutil.ReadAll(response.Body)
	if err != nil {
		logrus.Fatal(err)
	}

	logrus.Infof("Slack Notification result: %v", string(body))
}

func SendSlackNotification(title string, text string, color string) {
	slackURL, slackURLSet := os.LookupEnv("SLACK_URL")

	if slackURLSet && (slackURL != "") {
		logrus.Infof("Slack URL is %v", slackURL)

		slackChannel := "general"
		channel, channelSet := os.LookupEnv("SLACK_CHANNEL")
		if channelSet && (channel != "") {
			slackChannel = channel
		}

		msgFields := slackMessageFields{
			Title:    title,
			Value:    text,
			Short:    false,
			Markdown: true,
		}

		msg := slackMessage{
			Fallback: msgFields.Title,
			Color:    color,
			Fields:   []slackMessageFields{msgFields},
		}

		payload, err := json.Marshal(slackWebhookPayload{
			Username:    "AWS IAM Access Key Manager",
			IconEmoji:   ":key:",
			Attachments: []slackMessage{msg},
			Channel:     slackChannel,
		})
		if err != nil {
			logrus.Fatal(err)
		}

		logrus.Infof("Attempting to send Slack message titled '%v' to channel #%v.", msgFields.Title, slackChannel)
		slackClient(slackURL, payload)
	} else {
		logrus.Warn("Environment variable 'SLACK_URL' is not set, Slack notifications have been disabled.")
	}
}

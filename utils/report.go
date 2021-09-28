package utils

import (
	"fmt"

	"github.com/sirupsen/logrus"
)

func ReportKeys() {
	reportedKeys := ExamineKeys()

	if len(reportedKeys.expireKeys) > 0 {
		notice := fmt.Sprintf("The following active keys exist beyond the expiration policy of %v days:\n", reportedKeys.expireKeys[0].expire)
		for _, key := range reportedKeys.expireKeys {
			notice = notice + key.eventMessage
		}

		logrus.Info(notice)
		SendSlackNotification("Expired IAM Access Keys", notice, "danger")
	}

	if len(reportedKeys.warnKeys) > 0 {
		notice := fmt.Sprintf("The following active keys are approaching expiration(%d days):\n", reportedKeys.expireKeys[0].expire)
		for _, key := range reportedKeys.warnKeys {
			notice = notice + key.eventMessage
		}

		logrus.Info(notice)
		SendSlackNotification("Soon to expire IAM Access Keys", notice, "warning")
	}
}

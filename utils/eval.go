package utils

import (
	"fmt"
	"os"
	"strconv"
	"time"

	"github.com/aws/aws-sdk-go-v2/service/iam/types"
	"github.com/sirupsen/logrus"
)

type expirationDates struct {
	warnDays, expireDays int
	warnDate, expireDate time.Time
}

type issueKey struct {
	keyData      types.AccessKeyMetadata
	eventMessage string
	warn, expire int
}

type issueReport struct {
	warnKeys, expireKeys []issueKey
}

func setDates() expirationDates {
	dates := expirationDates{}
	warnDays := 85
	expireDays := 90

	warnStr, warnSet := os.LookupEnv("WARN_DAYS")
	expStr, expSet := os.LookupEnv("EXPIRE_DAYS")

	if warnSet && (warnStr != "") {
		warnDays, _ = strconv.Atoi(warnStr)
	}
	if expSet && (expStr != "") {
		expireDays, _ = strconv.Atoi(expStr)
	}

	logrus.Infof("WARNING set for key age >= %v days and < %v days.", warnDays, expireDays)
	logrus.Infof("EXPIRE set to key age >= %v days.", expireDays)

	rightNow := time.Now().UTC()
	dates.warnDate = rightNow.AddDate(0, 0, -warnDays)
	dates.expireDate = rightNow.AddDate(0, 0, -expireDays)
	dates.warnDays = warnDays
	dates.expireDays = expireDays

	return dates
}

func ExamineKeys() issueReport {
	var activeAccessKeys []types.AccessKeyMetadata
	reportKeys := issueReport{}
	evalDates := setDates()
	iamUsers := AcctIAMUsers()

	for _, user := range iamUsers {
		userKeys := GetAccessKeys(user)
		activeAccessKeys = append(activeAccessKeys, userKeys...)
	}

	for _, key := range activeAccessKeys {
		warnDiff := (evalDates.warnDate.Sub(*key.CreateDate).Hours() / 24)
		expDiff := (evalDates.expireDate.Sub(*key.CreateDate).Hours() / 24)

		if int(expDiff) >= evalDates.expireDays {
			expKey := issueKey{
				keyData:      key,
				eventMessage: fmt.Sprintf("User: %v\nKey Id: *%v* (%v days)\n\n", *key.UserName, *key.AccessKeyId, (int(expDiff) - evalDates.expireDays)),
				warn:         evalDates.warnDays,
			}
			reportKeys.expireKeys = append(reportKeys.expireKeys, expKey)
		} else if int(warnDiff) >= evalDates.warnDays {
			warnKey := issueKey{
				keyData:      key,
				eventMessage: fmt.Sprintf("User: *%v*\tKey Id: *%v* (%v days remaining)\n\n", *key.UserName, *key.AccessKeyId, (evalDates.expireDays - int(warnDiff))),
				expire:       evalDates.expireDays,
			}
			reportKeys.warnKeys = append(reportKeys.warnKeys, warnKey)
		} else {
			logrus.Printf("Key: %v User: %v", *key.AccessKeyId, *key.UserName)
		}
	}

	return reportKeys
}

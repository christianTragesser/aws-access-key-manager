package utils

import (
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

type issueKeys struct {
	warnKeys, expireKeys []types.AccessKeyMetadata
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

	logrus.Printf("Warn days: %v", warnDays)
	logrus.Printf("Expire days: %v", expireDays)

	rightNow := time.Now().UTC()
	dates.warnDate = rightNow.AddDate(0, 0, -warnDays)
	dates.expireDate = rightNow.AddDate(0, 0, -expireDays)
	dates.warnDays = warnDays
	dates.expireDays = expireDays

	return dates
}

func ExamineKeys() issueKeys {
	var activeAccessKeys []types.AccessKeyMetadata
	reportKeys := issueKeys{}
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
			reportKeys.expireKeys = append(reportKeys.expireKeys, key)
			logrus.Printf("EXPIRED - Key: %v (%v days expired) User: %v", *key.AccessKeyId, (int(expDiff) - evalDates.expireDays), *key.UserName)
		} else if int(warnDiff) >= evalDates.warnDays {
			reportKeys.warnKeys = append(reportKeys.warnKeys, key)
			logrus.Printf("WARN - Key: %v (%v days remaining) User: %v", *key.AccessKeyId, (evalDates.expireDays - int(warnDiff)), *key.UserName)
		} else {
			logrus.Printf("Key: %v User: %v", *key.AccessKeyId, *key.UserName)
		}
	}

	return reportKeys
}

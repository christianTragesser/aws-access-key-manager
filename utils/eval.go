package utils

import (
	"fmt"
	"os"
	"strconv"
	"strings"
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
	expire       int
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
	if expireDays <= warnDays {
		logrus.Fatal("Invalid expire value. Warning threshold value must be less than expire threshold value.")
	}

	rightNow := time.Now().UTC()
	dates.warnDate = rightNow.AddDate(0, 0, -warnDays)
	dates.expireDate = rightNow.AddDate(0, 0, -expireDays)
	dates.warnDays = warnDays
	dates.expireDays = expireDays

	logrus.Infof("EXPIRE set to %v days - %v", expireDays, dates.expireDate.Format(time.UnixDate))
	logrus.Infof("WARNING set for %v days - %v", warnDays, dates.warnDate.Format(time.UnixDate))

	return dates
}

func ExamineKeys() issueReport {
	disable, disableSet := os.LookupEnv("KEY_DISABLE")
	if disableSet {
		disable = strings.ToUpper(disable)
	}
	var activeAccessKeys []types.AccessKeyMetadata
	reportKeys := issueReport{}

	// get expire and warn dates
	evalDates := setDates()
	iamUsers := AcctIAMUsers()

	// get all active IAM keys
	for _, user := range iamUsers {
		userKeys := GetAccessKeys(user)
		activeAccessKeys = append(activeAccessKeys, userKeys...)
	}

	// evaluate each active key
	for _, key := range activeAccessKeys {
		warnDiff := (evalDates.warnDate.Sub(*key.CreateDate).Hours() / 24)
		expDiff := (evalDates.expireDate.Sub(*key.CreateDate).Hours() / 24)

		// report expired key if older than expire date
		if int(expDiff) >= evalDates.expireDays {
			expKey := issueKey{
				keyData:      key,
				eventMessage: fmt.Sprintf("User: %v - Key Id: *%v* (%v days expired)\n", *key.UserName, *key.AccessKeyId, int(expDiff)),
				expire:       evalDates.expireDays,
			}
			if disableSet && (disable == "TRUE") {
				DisableKey(key)
				disableMsg := fmt.Sprintf("Key %v has been *disabled*\n\n", *key.AccessKeyId)
				expKey.eventMessage = expKey.eventMessage + disableMsg
			}

			reportKeys.expireKeys = append(reportKeys.expireKeys, expKey)

		} else if (int(warnDiff) >= evalDates.warnDays) && (int(expDiff) < evalDates.expireDays) {
			// report warning for keys younger than expire date but older than warn date
			daysRemaining := (evalDates.expireDays - int(expDiff))

			warnKey := issueKey{
				keyData:      key,
				eventMessage: fmt.Sprintf("User: %v - Key Id: *%v* (%v days remaining)\n\n", *key.UserName, *key.AccessKeyId, int(daysRemaining)),
				expire:       evalDates.expireDays,
			}
			reportKeys.warnKeys = append(reportKeys.warnKeys, warnKey)
		} else if int(expDiff) < evalDates.expireDays {
			// report valid if younger than expire date
			logrus.Infof("Valid Key Age - User: %v Key: %v", *key.UserName, *key.AccessKeyId)
		} else {
			logrus.Warnf("Unmanaged result - User: %v Key: %v Created: %v", *key.UserName, *key.AccessKeyId, *key.CreateDate)
		}
	}

	return reportKeys
}

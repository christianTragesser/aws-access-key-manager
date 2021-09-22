package utils

import (
	"context"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/iam"
	"github.com/aws/aws-sdk-go-v2/service/iam/types"
	"github.com/sirupsen/logrus"
)

type IAMAPI interface {
	ListUsers(ctx context.Context, params *iam.ListUsersInput, optFns ...func(*iam.Options)) (*iam.ListUsersOutput, error)
	ListAccessKeys(ctx context.Context, params *iam.ListAccessKeysInput, optFns ...func(*iam.Options)) (*iam.ListAccessKeysOutput, error)
}

func ListUsers(c context.Context, api IAMAPI) (*iam.ListUsersOutput, error) {
	input := &iam.ListUsersInput{
		MaxItems: aws.Int32(int32(100)),
	}
	return api.ListUsers(c, input)
}

func ListAccessKeys(c context.Context, api IAMAPI, username string) (*iam.ListAccessKeysOutput, error) {
	input := &iam.ListAccessKeysInput{
		MaxItems: aws.Int32(int32(100)),
		UserName: &username,
	}
	return api.ListAccessKeys(c, input)
}

func AcctIAMUsers() []string {
	cfg, err := config.LoadDefaultConfig(context.TODO())
	if err != nil {
		logrus.Fatal(err)
		panic(err)
	}

	iamClient := iam.NewFromConfig(cfg)

	request, err := ListUsers(context.TODO(), iamClient)
	if err != nil {
		logrus.Fatal(err)
		panic(err)
	}

	var users []string

	for i := 0; i < len(request.Users); i++ {
		users = append(users, *request.Users[i].UserName)
	}

	return users
}

func GetAccessKeys(userName string) []types.AccessKeyMetadata {
	cfg, err := config.LoadDefaultConfig(context.TODO())
	if err != nil {
		logrus.Fatal(err)
		panic(err)
	}

	iamClient := iam.NewFromConfig(cfg)

	result, err := ListAccessKeys(context.TODO(), iamClient, userName)
	if err != nil {
		logrus.Fatal(err)
		panic(err)
	}

	var activeKeys []types.AccessKeyMetadata
	for _, key := range result.AccessKeyMetadata {
		if string(key.Status) == "Active" {
			activeKeys = append(activeKeys, key)
		}
	}

	return activeKeys
}

FROM docker.io/library/golang:alpine AS build

RUN apk update && apk add --no-cache git ca-certificates tzdata && \
    update-ca-certificates && \
    adduser --disabled-password --gecos "" \
    --home "/none" --no-create-home \
    --shell "/sbin/nologin" --uid "2222" "keyman"

WORKDIR $GOPATH/src/github.com/christiantragesser/aws-access-key-manager
ADD go.mod .
ADD go.sum .
ADD main.go .
COPY utils ./utils 

RUN go get -d -v

RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build \
    -ldflags='-w -s -extldflags "-static"' -a \
    -o /go/bin/aws-access-key-manager-amd64-linux .

RUN CGO_ENABLED=0 GOOS=darwin GOARCH=amd64 go build \
    -ldflags='-w -s -extldflags "-static"' -a \
    -o /go/bin/aws-access-key-manager-amd64-darwin .

RUN CGO_ENABLED=0 GOOS=darwin GOARCH=amd64 go build \
    -ldflags='-w -s -extldflags "-static"' -a \
    -o /go/bin/aws-access-key-manager-amd64.exe .

FROM scratch AS linux-binary
COPY --from=build /go/bin/aws-access-key-manager-amd64-linux /aws-access-key-manager-amd64-linux

FROM scratch AS macos-binary
COPY --from=build /go/bin/aws-access-key-manager-amd64-darwin /aws-access-key-manager-amd64-darwin

FROM scratch AS windows-binary
COPY --from=build /go/bin/aws-access-key-manager-amd64.exe /aws-access-key-manager-amd64.exe

FROM scratch as container
COPY --from=build /usr/share/zoneinfo /usr/share/zoneinfo
COPY --from=build /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=build /etc/passwd /etc/passwd
COPY --from=build /etc/group /etc/group
COPY --from=build /go/bin/aws-access-key-manager-amd64-linux /go/bin/aws-access-key-manager

USER keyman

ENTRYPOINT ["/go/bin/aws-access-key-manager"]
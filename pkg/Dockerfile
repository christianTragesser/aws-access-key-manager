# Supply source and dependenies
FROM docker.io/library/golang:alpine AS source

RUN apk add --no-cache git ca-certificates tzdata && \
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


# Build platform specific binaries
FROM source AS linux-build
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build \
    -ldflags='-w -s -extldflags "-static"' -a \
    -o /go/bin/aws-access-key-manager-amd64-linux .

FROM source AS macos-build
RUN CGO_ENABLED=0 GOOS=darwin GOARCH=amd64 go build \
    -ldflags='-w -s -extldflags "-static"' -a \
    -o /go/bin/aws-access-key-manager-amd64-darwin .

FROM source AS windows-build
RUN CGO_ENABLED=0 GOOS=windows GOARCH=amd64 go build \
    -ldflags='-w -s -extldflags "-static"' -a \
    -o /go/bin/aws-access-key-manager-amd64.exe .


# Extract binary artifacts to delivery pipeline host
FROM scratch AS linux-binary
COPY --from=linux-build /go/bin/aws-access-key-manager-amd64-linux /aws-access-key-manager-amd64-linux

FROM scratch AS macos-binary
COPY --from=macos-build /go/bin/aws-access-key-manager-amd64-darwin /aws-access-key-manager-amd64-darwin

FROM scratch AS windows-binary
COPY --from=windows-build /go/bin/aws-access-key-manager-amd64.exe /aws-access-key-manager-amd64.exe


# Build container image
FROM scratch as container
COPY --from=source /usr/share/zoneinfo /usr/share/zoneinfo
COPY --from=source /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=source /etc/passwd /etc/passwd
COPY --from=source /etc/group /etc/group
COPY --from=linux-build /go/bin/aws-access-key-manager-amd64-linux /go/bin/aws-access-key-manager

USER keyman

ENTRYPOINT ["/go/bin/aws-access-key-manager"]
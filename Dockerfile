FROM --platform=$TARGETPLATFORM golang:1.21.2-alpine AS build

WORKDIR /app
COPY . .

RUN go mod download && go mod verify
RUN go build -o FakeCourseBook

FROM --platform=$TARGETPLATFORM alpine:latest

WORKDIR /app
COPY --from=build /app/FakeCourseBook .
COPY --from=build /app/config.json .

CMD ["./FakeCourseBook"]
TARGET ?= kindlehf
BUILD_TYPE ?= release

.PHONY: native run debug previews build package check

native:
	./scripts/build.sh native debug

run:
	./scripts/run-native.sh

debug:
	./scripts/debug-native.sh

previews:
	./scripts/capture-previews.sh

build:
	./scripts/build.sh $(TARGET) $(BUILD_TYPE)

package: build
	./scripts/package.sh $(TARGET)

check:
	./scripts/check.sh $(TARGET)

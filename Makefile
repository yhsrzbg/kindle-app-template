TARGET ?= kindlehf
BUILD_TYPE ?= release

.PHONY: native run debug build package check

native:
	./scripts/build.sh native debug

run:
	./scripts/run-native.sh

debug:
	./scripts/debug-native.sh

build:
	./scripts/build.sh $(TARGET) $(BUILD_TYPE)

package: build
	./scripts/package.sh $(TARGET)

check:
	./scripts/check.sh $(TARGET)

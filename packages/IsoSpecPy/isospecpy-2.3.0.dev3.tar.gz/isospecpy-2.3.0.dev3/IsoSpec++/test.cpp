#include "isoSpec++.h"

int main() {
    auto orderedGenerator = IsoSpec::IsoOrderedGenerator("H2O1");
    orderedGenerator.advanceToNextConfiguration();
}

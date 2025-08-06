#include "llvm/Pass.h"
#include "llvm/IR/Module.h"
#include "llvm/IR/Function.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/Demangle/Demangle.h"

using namespace llvm;

namespace {

struct HelloPass : public PassInfoMixin<HelloPass> {
    PreservedAnalyses run(Function &F, FunctionAnalysisManager &AM) {
        StringRef mangled = F.getName();
        std::string demangled = llvm::demangle(mangled.str());
        errs() << F.getName() << " -> " << demangled << "\n";
        return PreservedAnalyses::all();
    };
};

}

extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo
llvmGetPassPluginInfo() {
    return {
        .APIVersion = LLVM_PLUGIN_API_VERSION,
        .PluginName = "Hello pass",
        .PluginVersion = "v0.1",
        .RegisterPassBuilderCallbacks = [](PassBuilder &PB) {
            // PB.registerPipelineStartEPCallback(
            //     [](ModulePassManager &MPM, OptimizationLevel Level) {
            //         MPM.addPass(HelloPass());
            //     });
            PB.registerPipelineParsingCallback(
            [](StringRef Name, FunctionPassManager &FPM,
                ArrayRef<PassBuilder::PipelineElement>) {
                    if (Name == "hello-fn") {
                        FPM.addPass(HelloPass());
                        return true;
                    }
                    return false;
            });
        }
    };
}
# Upstream framework

CodeVerifier is implemented as an extension of [ms-swift](https://github.com/modelscope/ms-swift). The framework is retained under `third_party/ms-swift` with its original Apache-2.0 license.

The CodeVerifier-specific modules implement the structured response contract, evidence projection, field-wise advantage routing, and paper-aligned configuration presets. They are intentionally separated from the framework so that the task logic can be inspected and reused independently.

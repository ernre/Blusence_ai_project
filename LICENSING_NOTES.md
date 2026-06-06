# Licensing Notes

VPE isolates proprietary or third-party services behind providers. The Fashn.ai
integration is used only for benchmarking and reference comparison.

Do not train VPE models on Fashn.ai outputs unless the applicable service terms
explicitly allow that use. Keep provider credentials in `.env` or a secret
manager, never in Git.

The IDM-VTON provider path is an open-source research baseline. The upstream
IDM-VTON code and checkpoints are published under CC BY-NC-SA 4.0, so do not
copy them into a proprietary/commercial product path without separate permission
or a licensing review. Use it to learn, benchmark, and validate architecture
choices while the proprietary VPE engine is developed separately.

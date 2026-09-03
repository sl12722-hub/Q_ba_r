# Agentic Alpha Research Skill V6.0.0

[English](README.md) | 简体中文

这是一个面向本地量化研究工厂的 Codex Skill，用于组织因子、机器学习
和深度学习策略的迭代、审计、回测与晋级。

它不是另一个单独的回测框架，而是位于现有研究项目之上的研究策略层：
约束数据协议、因果边界、实验契约、样本外预测、容量测试和 Champion /
Challenger 晋级，避免把偶然高分或协议错误误判成稳定 Alpha。

本仓库不包含行情数据、训练模型、私有因子结果或交易引擎。

## V6.0 主要能力

- 在模型比较和集成前校验完整实验契约。
- 分析模型在各折上的失效一致性，及时终止无效的集成权重搜索。
- 当静态特征共同失效时，路由至严格因果的 Rank Innovation 表征。
- 对窗口、预测周期、滞后和模型规格执行有序邻域稳定性检查。
- 审计不可变 OOF 预测、交易尾部一致性和模型目标邻域。
- 使用 GPU 批量执行完整容量策略矩阵，并要求 CPU 对照验证。
- 将研究组合原始策略作为容量测试锚点，禁止通过降低门槛挽救结果。
- 默认失败关闭：诊断指标优秀但容量、数据或因果门槛失败时不予晋级。

## 目录结构

```text
agentic-alpha-research/
|-- SKILL.md                       Skill 入口与核心研究协议
|-- VERSION                        当前稳定版本
|-- CHANGELOG.md                   版本演进记录
|-- agents/openai.yaml             Codex 展示与调用配置
|-- references/                    详细研究协议
|-- scripts/                       确定性审计工具
|-- tests/                         Skill 回归测试
`-- docs/PROMOTION_EVIDENCE_V6.0.md
```

## 安装

将本发布包目录中的内容复制到：

```text
%USERPROFILE%\.codex\skills\agentic-alpha-research
```

安装后的目录名应保持为 `agentic-alpha-research`，且 `SKILL.md` 应位于该目录
顶层。重新加载 Codex 后，可以自动触发该 Skill，也可以显式使用
`$agentic-alpha-research`。

## 接入本地研究项目

1. 编辑 `references/local-project.md`。
2. 配置研究项目、Python 环境和数据目录。
3. 由项目提供因子执行、模型训练、回测以及 `agentic_alpha` Python 包。
4. 在开展实验前运行数据源审计和 protocol doctor。

Skill 中部分审计脚本仅使用 Python 标准库。面板和 OOF 审计还需要项目
环境中的 `numpy`、`pandas` 和 `pyarrow`。

## 验证

在仓库根目录执行：

```powershell
python -m unittest discover -s tests -v
python path\to\skill-creator\scripts\quick_validate.py .
```

V6.0 晋级时通过了 16 项 Skill 测试和 70 项项目测试。完整的版本证据和
容量近失案例记录在 `docs/PROMOTION_EVIDENCE_V6.0.md`。

## 研究边界

- 本地 IC、Sharpe 和收益指标不代表任何平台官方结果。
- 本项目不承诺投资收益或排行榜分数。
- 诊断候选必须继续通过数据、因果、成本和容量门槛才能成为可执行候选。
- BigQuant AIStudio 提交文件合规检查不属于本 Skill 的职责范围。

## 发布完整性

`MANIFEST.sha256` 记录发布包中的全部文件哈希。通过压缩包分发时，应在
安装前核对清单与压缩包 SHA256。

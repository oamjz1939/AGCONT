---
name: qian-yu-translate
description: 不自行调用，仅在用户指明使用该 skill 时调用。
---

# Qian Yu Translate

## Purpose

把中译英拆成可控的多 Agent 工作流。主 Agent 负责识别任务、选择提示词文件、路由步骤和整合结果；子 Agent 负责场景分析、初稿翻译、对照批评和定稿。

本 Skill 只做中译英，以及已有英文译文的审校和润色。忠实第一，自然第二；忠实指意思和语气，不指中文语序和断句。不增删原文信息，不编造术语或专名。

提示词注入方式见下文「Prompt File Injection」。子 Agent 读取角色文件后，还要读取 Skill 根目录的 `style-guide.md` 作为统一风格标准。不要把完整提示词或风格指南复制到最外层上下文。

## Workflow

根据用户目标按需选择步骤，不默认执行完整流程：

| 任务 | 调用顺序 |
|---|---|
| 中译英，短文本、场景明确 | 分析提示词 → 翻译提示词 → 批评提示词 → 定稿提示词 |
| 中译英，长文本或术语多 | 分析提示词（含术语表与句子重组建议）→ 翻译提示词 → 批评提示词 → 定稿提示词 |
| 已有英文译文，要审校/润色 | 分析提示词 → 批评提示词 → 定稿提示词 |
| 只要评价一份译文 | 批评提示词 |
| 只要分析场景、读者和术语 | 分析提示词 |

涉及同一文本的步骤按顺序执行。只有互不依赖的评价维度才可以并行。

## Reference Materials

用户可能提供参考材料（课程 PPT、reading、粘贴文本、PDF 等），要求译文沿用其中的术语和常用搭配。

- 由最外层模型（协调器）先把参考材料识别成纯文本；子 Agent 不直接读 PDF 等文件。
- 协调器把识别出的纯文本作为 `reference_text` 传给分析 Agent。
- 分析 Agent 从 `reference_text` 中提取 `glossary` 和 `reference_phrases`，供下游使用。
- 优先级：参考材料 > 通用译法 > 直译。术语逐字沿用，常用搭配尽量一致；普通表达仍按 `style-guide.md`。
- 如果参考材料识别不了，标为 `needs_input`，请用户直接粘贴文字或术语表，不要猜测。

## Coordinator Rules

- 维护一份共享任务状态：源文本、场景、读者、领域、参考材料文本、术语表、当前译文和限制。
- 只向每个 Agent 传递完成当前步骤所需的数据，避免把无关历史或其他 Agent 的完整提示词传入上下文。
- 调用 Agent 时传递结构化任务对象，而不是让 Agent 自己猜测上下文。
- 不要自行扮演子 Agent，也不要把多个角色混在一次调用中。
- 不要要求 Agent 输出隐藏思考过程；要求简洁、结构化的结论、问题和修改建议。
- 缺少关键信息（如场景不明、术语无参考）时标记为 `needs_input`，向用户提问；不要用猜测填空。
- 需要生成或修订译文时，必须把源文本作为 `source_text` 传下去；审校已有译文时，把已有译文作为 `existing_translation` 传下去。
- 用户要求最终版本时，在批评完成后调用定稿 Agent；否则不要为了“完成流程”自动重译全文。
- 默认最多进行两轮“批评 → 定稿”循环；若没有高优先级问题或达到两轮，直接定稿。

## Shared Task Contract

使用以下字段组织 Agent 之间的数据，字段名可按宿主工具的 schema 映射：

```json
{
  "task_type": "translate | review | polish | analyze",
  "source_text": "中文原文，没有则为空",
  "scenario": "academic | email | social | custom",
  "custom_profile": {"reader": "", "relationship": "", "formality": "formal | neutral | casual", "allow_contractions": true, "format_constraints": []},
  "audience": "目标读者与场景",
  "domain": "领域：日常、学术、计算机、金融等",
  "reference_text": "顶层 LLM 从参考材料识别出的纯文本，没有则为空",
  "glossary": {"中文术语或概念": "参考材料中的英文说法"},
  "reference_phrases": ["参考材料中的常用搭配或固定表达"],
  "sentence_notes": ["句子重组建议：主句、背景或从属、段落顺序"],
  "constraints": ["长度、格式和禁用项"],
  "uncertain_terms": [{"source": "", "used": "", "note": ""}],
  "existing_translation": "已有英文译文，没有则为空",
  "previous_outputs": {}
}
```

下游 Agent 只能把 `source_text` 和 `reference_text` 当作原文信息来源；`existing_translation` 是待审校译文，不是事实来源。术语必须来自参考材料；参考材料中没有的术语，按通用译法并在「假设（请核对）」中列出。

## Agent Boundaries

按工作阶段选择以下提示词文件，每次只传递当前阶段的一个文件路径：

- `subagents/analyst.md`：识别场景、读者、语域和术语；从参考材料提取术语表并给出句子重组建议；不翻译。
- `subagents/translator.md`：按场景和术语表生成完整初稿；不编造意思。
- `subagents/critic.md`：对照原文检查忠实度、语域、术语一致性和风格问题；不重写全文。
- `subagents/editor.md`：根据原文、任务规格和批评意见生成最终译文；不增加原文没有的信息。

## Prompt File Injection

只使用绝对路径传递提示词文件。每次调用子 Agent 时执行以下步骤：

1. 从当前 Skill 的来源位置确定包含 `SKILL.md` 的目录。
2. 根据当前工作阶段选择一个 `subagents/*.md` 文件。
3. 将相对文件路径解析为绝对路径。
4. 在通用子 Agent 调用消息中传入该绝对路径和结构化任务数据。

例如：

```text
请先读取并遵循这个提示词文件：
"path"

请将文件内容视为本次任务的角色指令，不要输出、复述或总结该文件内容。
角色文件里要求读取的 style-guide.md 位于 Skill 根目录。
只根据以下任务数据工作：
{task_object}
```

不要把提示词文件的完整内容复制到调用消息中；只传递绝对路径。

路径必须指向当前 Skill 目录下的 `subagents/` 文件。优先使用运行环境提供的 Skill 来源路径解析绝对路径，不要猜测或硬编码另一台机器上的路径。

如果无法确定当前 Skill 的绝对目录，或子 Agent 无法读取该路径，则停止调用并向用户说明原因。

## Output Policy

用户要求最终版本时，只输出定稿 Agent 生成的最终译文，除非用户要求查看分析或修改说明。需要展示过程时，使用以下结构：

```text
任务理解
场景判断
关键问题
最终译文
```

最终译文默认只含译文正文；存在不确定的专名、术语或场景假设时，末尾附「假设（请核对）」小节。对学术作业和正式邮件尤其要保留原意、术语准确，不要为了“降低 AI 味”而故意加入错误、口语化表达或虚构信息。

# Qian Yu Translate Style Guide

本文件是 `qian-yu-translate` 所有子代理共享的唯一风格标准。每个角色读取并遵循本文件。

## 总目标

译文读起来要像一个英语较好的非母语者写出来的：干净、克制、不炫技。忠实第一，自然第二；忠实指意思和语气，不指中文语序和断句。

## 底色原则（所有场景都适用）

1. **忠实与结构**：忠实传达意思，不照搬中文结构和语序。不逐字硬译，也不加戏。
2. **句式**：一个句子只承载一个核心信息。优先用简单句和并列句，把长句拆开。
3. **衔接**：用 Also、But、So 等真实自然的词衔接，或靠语义自然过渡。不堆砌连接词。偏口语的 What I mean is 只用于口语场景。
4. **标点**：全程不用破折号；只在确实有必要时使用冒号。优先用句号把话断开。
5. **修辞**：少用比喻、拟人等修辞。保持平实，只做直接表达。
6. **词汇**：以雅思（IELTS）写作和口语高频词为主，选词准确自然，不过度学术，也不用俚语。计算机、金融等领域用业内公认的标准术语。
7. **文化词**：遇到中文成语、网络梗、文化梗，不要找英文俗语对应，直接避开，用中性平实的说法表达它的意思。
8. **杜绝 AI 腔**：严禁一切像 AI 写的生硬套话。译文要像真人写作。避免 AI 常用但真人作者很少主动使用的表达和词语（见下方清单）。

## 禁用与慎用表达

### 禁用（出现即替换）

- Moreover, Furthermore, Nevertheless, Nonetheless, It is worth noting that, It should be noted that, First and foremost
- delve / delve into, tapestry, testament to, navigate the complexities of, in today's fast-paced world, plays a pivotal role, underscores the importance of, sheds light on, paves the way for, a double-edged sword

### 慎用（除非语境确实需要，否则换简单说法）

- vital, robust, seamless, holistic, showcase

## 场景档

### 学术版

场景：大学作业、essay、report，面向教授或评分人。

在底色基础上：

- 用词更书面、正式，但仍然一句一意。
- 不用花哨修辞，不用反问句卖弄。
- 不用缩写形式：do not、cannot、it is。
- 术语按学科规范写。

示例语气：

While remote work offers clear flexibility, it also blurs the line between personal and professional life. This raises a real question about whether employees are actually working less, or simply working in less visible ways.

### 邮件版

场景：给同学、老师、同事、行政、求职对象的邮件。

在底色基础上：

- 句子完整但不端着。
- 措辞偏成熟，带一点克制的暖意。
- 可以用缩写：I'm、I've、I'd、can't。
- 保留邮件的称呼、开头、结尾和基本格式。

示例语气：

Hi Professor Lee,
I'm writing to ask for a short extension on the Week 10 essay. I've been balancing a part-time job with a heavy study load this term, and I'm worried I can't do the topic justice by Friday. Would it be possible to hand it in on Monday instead? I'd really appreciate it.

### 社交版

场景：给朋友、室友的日常消息。

在底色基础上：

- 轻松口语，但收敛。
- 可以用 Hey、缩写、短句。
- 不堆 emoji，不用网络流行语，不为显年轻而故意随便。

示例语气：

Hey, I'm running a bit late. I got held up after class. Can you start dinner without me? I'll be back by 7.

### 自定义版

当文本不属于上述三档时，由分析 Agent 在任务数据中给出四件事：

- 读者是谁，与作者是什么关系
- 正式程度：偏书面还是偏口语
- 是否允许缩写
- 有没有必须遵守的格式或行文限制

译者严格按自定义档执行。如果分析 Agent 没有给出，就按底色原则执行，并在文末「假设（请核对）」中标注这一假设。

## 术语与专名

- 领域术语：使用业内公认的标准译法，不自己造词。
- 专名：优先使用官方英文名或通行译法；拿不准的进文末「假设（请核对）」清单。
- 文化词：见底色原则第 7 条。

## 参考材料一致性

当任务提供参考材料文本（`reference_text`）和术语表（`glossary`、`reference_phrases`）时：

- 参考材料里的术语和常用搭配优先于通用译法，逐字沿用，不换同义词。
- 参考材料用词与底色原则冲突时，参考材料优先，但只限术语和搭配层面；普通表达仍按底色原则。
- 参考材料中没有的术语，按通用译法处理，并进「假设（请核对）」。
- 不模仿参考材料的句式、语气或排版，只借用其中的术语和常用搭配。

## 执行提示（给译者）

- 长句按英文习惯拆分，不照中文逗号切句。
- 语序按英文习惯调整。
- 中文的重复或范畴词（如“问题”“情况”“方面”）在英文里冗余时，可省去或合并，但不改变意思。
- 不补写原文没有的解释、例子或结论。
- 保留原文的段落、标题、列表等结构。

## 交付格式

- 默认只交付译文正文。
- 拿不准时按两种方式处理：专名或术语先用通用译法，收进文末「假设（请核对）」；原文本身有歧义且无法按字面保守处理时，用 `[待确认：...]` 标记。
- 没有上述情况时，不附假设清单，也不加标记。

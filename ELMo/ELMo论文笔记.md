### Deep contextualized word representations
#### 摘要：
我们引入了一种新型的深层语境化词语表示，它模拟了词汇使用的复杂特征(语法和语义)，以及这些用法如何在不同语境中变化(建模多义词)。我们的词向量是通过深度双向语言模型(bidirectional language model, biLM)的内部状态函数学习出来的，在大型文本语料中预训练的。在问答，文本推理和情感分析等任务中取得SOTA。我们还展示了一个分析表明，暴露深层预训练网络的内部结构是至关重要的，这允许下游模型混合不同类型的半监督信号。
#### 介绍：
预训练的词向量是许多神经语言理解模型的关键组成部分。 但是，学习高质量的表示可能具有挑战性。 它们应理想地模拟（1）**单词使用的复杂特征**（例如，语法和语义），以及（2）**这些使用如何在语言上下文中变化**（即，建模多义词）。在本文中，我们介绍了一种新型的深层语境化的单词表示，可以直接解决这两个挑战，可以轻松地集成到现有模型中。
我们的单词表示和传统的词向量不同，每一个标记都赋予了一个表示，这个表示是整个输入句子的一个函数。我们使用来自双向LSTM通过一对语言模型基于大量文本语料训练而出的向量表示。因此，我们称他们为**ELMo**(Embeddings from Language Models)。ELMo表示是深层的，因为它们是biLM的所有内层的一个函数，更确切地说，我们学习了每个输入单词上方堆叠的向量的线性组合，这明显提高了性能。
以这种方式组合内部状态可以得到非常丰富的单词表示。我们表明了更高级别的LSTM状态捕获了词义的上下文相关方面，而较低级别的状态建模了语法方面。说明这些所有的信号都是非常有用的。

#### ELMo: Embeddings from Language Models

##### ELMo
ELMo是双向语言模型内层表示的一种特殊的组合方式。对于每一个标记，一个L层的biLM计算了2L+1个表示的集合。

![avatar](https://github.com/coderGray1296/NLP/blob/master/ELMo/pictures/1.png)

我们计算一个任务的特殊权重通过所有biLM的层：

![avatar](https://github.com/coderGray1296/NLP/blob/master/ELMo/pictures/2.png)

考虑到每个biLM层具有不同的分布，在某种情况下，这还有助于每层**layer normalization**在计算权重之前。

##### 使用biLMs完成监督的NLP任务
给定一个预训练的biLM和一个目标NLP任务的监督框架，使用biLM来改进恩物模型是一个简单的过程。只需要运行biLM然后记录所有层对于每个单词的表示。然后让目标任务模型去学习这些表示的线性组合方式。
首先考虑没有biLM的监督模型的最底层。大多数的监督NLP模型都分享一个公共结构在最底层，允许我们以统一的方式添加ELMo。给定一句标记，使用预训练的单词嵌入和可选的基于字符的表示来形成每个标记位置的上下文无关的表示是一种标准的方式。然后模型形成了上下文敏感的表示hk，通常使用双向RNN，CNN或者前馈网络。
为了将ELMo添加进监督模型，我们先**freeze**住biLM的权重，然后聚合ELMo向量和输入xk，最终传递增强了表示的ELMo向量给任务RNN。**我们通过在任务RNN的输出同样引入ELMo**来观察进一步的改进，通过引入另一组输出特定线性权重，并替换掉hk。监督模型的其他部分仍然没有改变，这些额外的部分能够在更复杂的网络模型中的文本发生。
最终，我们发现引入中等数量的dropout给ELMo是有帮助的，而且在一些情况下通过添加loss去正则化ELMo的权重也是有帮助的。这引入了归纳bias给ELMo的权重去保持对所有biLM层平均值的相似度。
##### 预训练的双向语言模型架构
本文预训练biLM改进为支持两个方向联合训练并在LSTM层之间添加残余连接。
biLM为每一个令牌提供三个表示层，包括由于纯字符输入而在训练集外部的表示。相比之下，传统的单词嵌入方法只为固定词汇表中的标记提供了一层表示。
一旦开始预训练，biLM就可以为任何任务计算表示。在某些情况下，在某些特定域的数据上微调biLM会导致困惑度显著下降，并且下游任务的性能会提高。可以可视为biLM的一种域转移。因此在大多数情况下，我们在下游任务中使用了微调的biLM。
#### biLM表示捕获的信息
由于添加ELMo仅仅提高了单词向量的任务性能，因此biLM的上下文表示必须编码通常对于未在单词向量捕获的对于NLP任务有用的信息。直观的说，biLM必须使用它们的上下文来消除单词的含义。再结合上下文表示的情况下，biLM能够在源句中消除词性和词义。
##### 词义消歧
给定一个句子，我们使用biLM表示去预测目标单词的意思通过使用简单的1临近方法。为此，我们首先使用biLM计算训练语料库中的所有单词的表示，然后取每一个意义的平均表示。在测试时，我们再一次使用biLM去计算对于给定目标单词的表示并从目标集合中获得最近邻的词义。
##### 词性标注
为了检验biLM是否捕获了基本语法，我们使用上下文表示作为线性分类器的输入，该分类器预测POS标签。由于线性分类器仅增加了少量的模型容量，因此这是对biLM表示的直接测试。
##### 对于监督任务的影响
总而言之，这些实验证实了biLM中的不同层代表着不同类型的信息，并且解释了为什么包含所有biLM层对于下游任务中的最高性能非常重要。因此biLM的表示更容易转移到**WSD**(词义消歧)和**POS**标签，有助于ELMo在下游任务中的表示。
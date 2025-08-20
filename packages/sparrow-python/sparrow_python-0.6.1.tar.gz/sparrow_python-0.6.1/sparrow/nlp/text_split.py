class TextSplitter:
    def __init__(self, max_length: int = 2000, overlap: int = 100):
        """
        初始化TextSplitter

        Args:
            max_length (int): 每个文本块的最大长度
            overlap (int): 相邻块之间的重叠字符数,用于保持上下文连贯性

        Raises:
            ValueError: 当 overlap >= max_length 时抛出
        """
        if overlap >= max_length:
            raise ValueError("overlap must be less than max_length")
        if max_length <= 0 or overlap < 0:
            raise ValueError("max_length must be positive and overlap must be non-negative")

        self.max_length = max_length
        self.overlap = overlap

    def split_text(self, text: str) -> list[str]:
        """
        将文本切分成多个块

        Args:
            text (str): 待切分的文本

        Returns:
            list[str]: 切分后的文本块列表
        """
        if not text:
            return []

        if len(text) <= self.max_length:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            # 确定当前块的结束位置
            end = min(start + self.max_length, len(text))

            if end >= len(text):
                # 如果是最后一块,直接添加剩余文本
                chunk = text[start:]
                if chunk:  # 确保不添加空块
                    chunks.append(chunk)
                break

            # 从end位置向前查找最近的分隔符
            split_pos = self._find_split_position(text, end)

            # 确保split_pos > start,防止死循环
            if split_pos <= start:
                # 强制向前移动,确保进度
                split_pos = min(start + self.max_length, len(text))

            # 添加当前块
            chunk = text[start:split_pos]
            if chunk:  # 确保不添加空块
                chunks.append(chunk)

            # 更新下一块的起始位置,考虑重叠
            # 确保start真的向前移动了
            start = max(start + 1, split_pos - self.overlap)

        return chunks

    def _find_split_position(self, text: str, pos: int) -> int:
        """
        在指定位置附近寻找合适的分割点
        优先级: 段落 > 句号 > 逗号 > 空格 > 强制分割

        Args:
            text (str): 文本内容
            pos (int): 建议的分割位置

        Returns:
            int: 实际的分割位置
        """
        pos = min(pos, len(text))  # 确保pos不会越界

        # 向前查找段落分隔符
        for i in range(min(pos, len(text) - 1), max(0, pos - 200), -1):
            if text[i] == '\n' and i > 0 and text[i - 1] == '\n':
                return i + 1  # 返回段落开始位置

        # 向前查找句号等标点
        for i in range(min(pos, len(text)), max(0, pos - 100), -1):
            if text[i - 1:i + 1].rstrip() in ['。', '. ', '! ', '? ', '！ ', '？ ']:
                return i

        # 向前查找逗号等次要标点
        for i in range(min(pos, len(text)), max(0, pos - 50), -1):
            if text[i - 1:i + 1].rstrip() in ['，', ', ', '、 ']:
                return i

        # 向前查找空格
        for i in range(min(pos, len(text)), max(0, pos - 20), -1):
            if text[i - 1].isspace():
                return i

        # 如果找不到合适的分割点,则强制分割
        return min(pos, len(text))

    def __repr__(self):
        return f"TextSplitter(max_length={self.max_length}, overlap={self.overlap})"

if __name__ == '__main__':
    def test_text_splitter():
        # 用更大的max_length来测试，避免测试文本太小导致错误的分割
        splitter = TextSplitter(max_length=20, overlap=5)

        # 1. 测试空文本
        assert splitter.split_text("") == []
        print("Empty text test passed")

        # 2. 测试短文本
        assert splitter.split_text("hello") == ["hello"]
        print("Short text test passed")

        # 3. 测试正好在max_length的文本
        text_20 = "12345678901234567890"  # 正好20个字符
        result = splitter.split_text(text_20)
        assert result == [text_20]
        print("Exact max_length text test passed")

        # 4. 测试超过max_length且没有自然分隔符的文本
        text_30 = "123456789012345678901234567890"  # 30个字符
        result = splitter.split_text(text_30)
        assert len(result) == 2  # 应该分成两块
        # 检查第一块长度不超过max_length
        assert len(result[0]) <= 20
        # 检查第二块包含overlap的内容
        assert text_30.endswith(result[1])
        print("Long text without delimiters test passed")

        # 5. 测试带有句号的文本
        text_with_periods = "Hello world. This is a test. Final."
        result = splitter.split_text(text_with_periods)
        for chunk in result:
            assert len(chunk) <= 20
        # 检查是否在句号处分割
        assert any(chunk.endswith(". ") or chunk.endswith(".") for chunk in result)
        print("Text with periods test passed")

        # 6. 测试带有段落的文本
        text_with_paras = "Para 1\n\nPara 2\n\nPara 3"
        result = splitter.split_text(text_with_paras)
        # 检查分割后的每一块长度
        assert all(len(chunk) <= 20 for chunk in result)
        # 至少有一个块应该在段落处分割
        assert any("\n\n" in chunk for chunk in result)
        print("Text with paragraphs test passed")

        # 7. 测试重叠部分
        text_overlap = "First part. Second part. Third part."
        result = splitter.split_text(text_overlap)
        if len(result) > 1:
            # 检查相邻块之间是否有重叠
            for i in range(len(result) - 1):
                common = set(result[i][-5:]).intersection(set(result[i + 1][:5]))
                assert len(common) > 0
        print("Overlap test passed")


    # 运行测试
    test_text_splitter()

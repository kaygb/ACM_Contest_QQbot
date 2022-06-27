# 定义节点
class Node(object):
    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value
        self.left = None
        self.right = None
        self.parent = None
        self.color = 0  # 默认黑色0，红色1


class RedBlackTree(object):

    def __init__(self):
        self.root = None

    # 设置节点为红色
    def set_red_color(self, node):
        if node is not None:
            node.color = 1

    # 设置节点为黑色
    def set_black_color(self, node):
        if node is not None:
            node.color = 0

    # 判断是否是红色节点
    def is_red_color(self, node):
        if node is not None:
            if node.color == 1:
                return True
            else:
                return False
        else:
            return False

    # 判断是否是黑色节点
    def is_black_color(self, node):
        if node is not None:
            if node.color == 0:
                return True
            else:
                return False
        else:
            return False

    # 得到爷爷节点
    def get_grandparent(self, node):
        if node is not None:
            if node == self.root:
                return None
            elif node.parent == self.root:
                return None
            else:
                return node.parent.parent
        else:
            return None

    # 得到叔叔节点
    def get_uncle(self, node):
        gdp = self.get_grandparent(node)
        if gdp:
            if gdp.left == node.parent:
                return gdp.right
            elif gdp.right == node.parent:
                return gdp.left
            else:
                return False
        else:
            return False

    # 中序遍历，打印顺序
    def in_order_print(self, node):
        if node is not None:
            self.in_order_print(node.left)
            if node.color == 0:
                color = '黑色'
            elif node.color == 1:
                color = '红色'
            print("节点值：{}，颜色：{},value：{}".format(node.key, color, node.value))
            self.in_order_print(node.right)

    # 前序遍历，打印顺序
    def in_front_print(self, node):
        if node is not None:
            if node.color == 0:
                color = '黑色'
            elif node.color == 1:
                color = '红色'
            print("节点值：{}，颜色：{},value：{}".format(node.key, color, node.value))
            self.in_front_print(node.left)
            self.in_front_print(node.right)

    # 外部公开插入节点
    def insert(self, key, value):
        node = Node(key, value)
        self.real_insert(node)

    # 内部真实插入节点
    def real_insert(self, node):
        # 插入必须是红色节点
        self.set_red_color(node)
        if self.root is not None:
            cur_node = self.root
            while cur_node is not None:
                if cur_node.key > node.key:
                    if cur_node.left is not None:

                        cur_node = cur_node.left
                    else:
                        print('插入左子树:{}'.format(node.key))
                        cur_node.left = node
                        node.parent = cur_node
                        break
                elif cur_node.key < node.key:
                    if cur_node.right is not None:
                        cur_node = cur_node.right
                    else:
                        print('插入右子树:{}'.format(node.key))
                        cur_node.right = node
                        node.parent = cur_node
                        break
                elif cur_node.key == node.key:
                    print('替代:{}'.format(node.key))
                    cur_node.value = node.value
                    break
        else:
            print('插入根节点:{}'.format(node.key))
            self.root = node

        self.insert_fix_up(node)

    # 1.插入节点为root， -----》root结点必为黑色
    # 2.插入节点的key已经存在， -----》直接替换(上面已经处理过)
    # 3.插入节点的父节点为黑色， -----》下面的结点不需要改变，红黑树依然平衡
    # 4.插入节点的父节点为红色(出现红红的情况)
    #     4.1：叔叔节点存在，并且为红色 -----》(父叔双红，将爸爸和叔叔染为黑色，将爷爷染色为红色，并且爷爷节点为当前节点，进行下一轮处理)
    #     4.2：叔叔节点不存在或者为黑色，父节点为爷爷节点的左子树
    #           4.2.1：插入节点为其父节点的左子节点(LL情况) -----》将爸爸染色为黑色，将爷爷染色为红色，然后以爷爷节点右旋
    #           4.2.1：插入节点为其父节点的右子节点(LR情况) -----》将爸爸节点进行一次左旋，得到LL双红情况，然后指定爸爸节点为当前节点进行下一轮处理
    #     4.3：叔叔节点不存在或者为黑色，父节点为爷爷节点的右子树
    #           4.3.1：插入节点为其父节点的右子节点(RR情况) -----》将爸爸染色为黑色，将爷爷染色为红色，然后以爷爷节点左旋
    #           4.3.1：插入节点为其父节点的左子节点(RL情况) -----》将爸爸节点进行一次右旋，得到RR双红情况，然后指定爸爸节点为当前节点进行下一轮处理
    def insert_fix_up(self, node):
        # 插入节点为root，root结点必为黑色
        if node == self.root:
            self.set_black_color(node)
        # 插入节点的父节点为红色(出现红红的情况)
        elif self.is_red_color(node.parent):
            print('----------红红的情况---------------{}'.format(node.key))
            grand_parent = self.get_grandparent(node)
            uncle = self.get_uncle(node)
            # 叔叔节点存在，并且为红色(父叔双红，将爸爸和叔叔染为黑色，将爷爷染色为红色，并且爷爷节点为当前节点，进行下一轮处理)
            if uncle and self.is_red_color(uncle):
                print('----------叔叔节点存在，并且为红色----：{}'.format(node.key))
                self.set_black_color(node.parent)
                self.set_black_color(uncle)
                self.set_red_color(grand_parent)
                self.insert_fix_up(grand_parent)
                return True
            # 叔叔节点不存在或者为黑色
            elif uncle == None or self.is_black_color(uncle):
                # 父节点为爷爷节点的左子树
                if node.parent == grand_parent.left:
                    # 插入节点为其父节点的左子节点(LL情况)-----》将爸爸染色为黑色，将爷爷染色为红色，然后以爷爷节点右旋
                    if node == node.parent.left:
                        print('----------叔叔节点不存在或者为黑色,左子树 LL----：{}'.format(node.key))
                        self.set_black_color(node.parent)
                        self.set_red_color(grand_parent)
                        self.right_rotate(grand_parent)
                    # 插入节点为其父节点的右子节点(LR情况) -----》将爸爸节点进行一次左旋，得到LL情况，然后指定爸爸节点为当前节点进行下一轮处理
                    elif node == node.parent.right:
                        print('----------叔叔节点不存在或者为黑色,左子树 LR----：{}'.format(node.key))
                        self.left_rotate(node.parent)
                        self.right_rotate(node.parent)
                    return True
                # 父节点为爷爷节点的右子树
                elif node.parent == grand_parent.right:
                    # 插入节点为其父节点的右子节点(RR情况) -----》将爸爸染色为黑色，将爷爷染色为红色，然后以爷爷节点左旋
                    if node == node.parent.right:
                        print('----------叔叔节点不存在或者为黑色,右子树 RR----：{}'.format(node.key))
                        self.set_black_color(node.parent)
                        self.set_red_color(grand_parent)
                        self.left_rotate(grand_parent)
                    # 插入节点为其父节点的左子节点(RL情况) -----》将爸爸节点进行一次右旋，得到RR双红情况，然后指定爸爸节点为当前节点进行下一轮处理
                    elif node == node.parent.left:
                        print('----------叔叔节点不存在或者为黑色,右子树 RL----：{}'.format(node.key))
                        self.right_rotate(node.parent)
                        self.left_rotate(node.parent)
                    return True
        else:
            return True

    # 左旋
    # 1.旧的父节点接收新父节点的左子树，新父节点的左子树也要指向旧的父节点
    # 2.新的父节点连接上旧的父节点的父母，旧的连接点的父母也要指向新的儿子（新的子连接父，父指新的子）
    # 3.将新的父节点与旧的父节点互指（互指的过程）
    def left_rotate(self, node):
        if node is not None:
            # 暂存新的父节点
            cur_right = node.right
            # 1.旧的父节点接收新父节点的左子树，新父节点的左子树也要指向旧的父节点
            node.right = cur_right.left
            if cur_right.left is not None:
                cur_right.left.parent = node

            # 2.新的父节点连接上旧的父节点的父母，旧的连接点的父母也要指向新的儿子（新的子连接父，父指新的子）
            if node.parent is not None:
                cur_right.parent = node.parent
                if node.parent.left == node:
                    node.parent.left = cur_right
                elif node.parent.right == node:
                    node.parent.right = cur_right
            else:
                # 如果旧的父节点是空，说明它是root，这时要把root变为新的父节点
                self.root = cur_right

            # 3.将新的父节点与旧的父节点互指（互指的过程）
            node.parent = cur_right
            cur_right.left = node

            return True

    # 右旋
    # 1.旧的父节点接收新父节点的右子树，新父节点的右子树也要指向旧的父节点
    # 2.新的父节点连接上旧的父节点的父母，旧的连接点的父母也要指向新的儿子（新的子连接父，父指新的子）
    # 3.将新的父节点与旧的父节点互指（互指的过程）
    def right_rotate(self, node):
        if node is not None:
            # 暂存新的父节点
            cur_left = node.left
            # 1.旧的父节点接收新父节点的右子树，新父节点的右子树也要指向旧的父节点
            if cur_left.right is not None:
                node.left = cur_left.right
                cur_left.right.parent = node

            # 2.新的父节点连接上旧的父节点的父母，旧的连接点的父母也要指向新的儿子（新的子连接父，父指新的子）
            if node.parent is not None:
                cur_left.parent = node.parent
                if node.parent.left == node:
                    node.parent.left = cur_left
                elif node.parent.right == node:
                    node.parent.right = cur_left
            else:
                self.root = cur_left

            # 3.将新的父节点与旧的父节点互指（互指的过程）
            node.parent = cur_left
            cur_left.right = node
            return True


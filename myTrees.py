import json 
import logging
import pysnmp

class TreeNode(object):
    def __init__(self, Value):
        self.value = Value
        self.children = []
        self.word_end = False
        self.leaf_value = None

class BasicTree(object):
    def __init__(self, NodeList=[]):
        self.root = TreeNode('*')
        if(not len(NodeList)):
            self.insert(NodeList)

    def print_tree(self, subtree=None, depth=0, prefix=""):
        if subtree==None :
            subtree = self.root
        
        if depth <= 0:
            print('\n>> Printing Tree...')
        else:
            prefix += ("."+str(subtree.value) )
            print(depth, prefix, subtree.leaf_value)
        depth += 1

        for child in subtree.children:
            self.print_tree(prefix=prefix, subtree=child, depth=depth)

        return None

    def insert(self, NodeList: list):
        logging.info('\n>> Inserting Nodes "{}"'.format(NodeList))
        node = self.root
        for v in NodeList:
            logging.debug('checking node = {}'.format(node.value))
            for child in node.children:
                if v == child.value:
                    logging.debug('"{}" is found!'.format(v))
                    node = child
                    break
            else:
                # add new node
                logging.debug('node "{}" not in tree, add!'.format(v))
                new_node = TreeNode(v)
                node.children.append(new_node)
                node = new_node

        # mark the node as ended
        node.word_end = True

        logging.info('NodeList "{}" is added!'.format(NodeList))
        return node

    def delete(self, NodeList:list):
        
        if not NodeList:
            logging.warning('\n>> Empty List Intput')
            return
        logging.info('\n>> Deleting : "{}"'.format(NodeList))

        # 1. check if existed
        logging.debug('>>> Check if the word exists')
        existed, nodes = self.look_up(NodeList)
        if not existed:
            print('NodeList "{}" not found'.format(NodeList))
            return

        # 2. if existed, start deleted
        logging.debug('>>> Start deleting')
        nodes[-2].children.remove(nodes[-1]) # remove specific element in a list

        for i in range(len(nodes)-2, 0, -1):
            # print('pos = {}, word_end? {}'.format(i, nodes[i].word_end))
            if nodes[i].word_end:
                break
            nodes[i-1].children.remove(nodes[i])

        return

# if word exist: return True and its nodes, else: return False and prefix_nodes
    def look_up(self, NodeList: list) -> (bool, list):
        logging.info('\n>> Looking up Nodes "{}"'.format(NodeList))
        node = self.root
        prefix = "" # for debug
        prefix_nodes = [self.root] # actual return value

        for v in NodeList:
            # print('checking node = {}'.format(w))
            for child in node.children:
                if v == child.value:
                    prefix += (str(v) + ",")
                    prefix_nodes.append(child)
                    node = child
                    break
            else:
                # word not found
                logging.warning('node "{}" is not found, the nearest prefix is "{}".'.format(v, prefix))

                return False, prefix_nodes

        logging.info('NodeList "{}" is found!'.format(NodeList))
        return True, prefix_nodes

class SnmpTree(BasicTree):
    def __init__(self, OID:str=""):
        NodeList = [int(i) for i in OID.split(".") if i]
        super().__init__(NodeList)
    def insert(self, OID, value=""):
        if type(OID) == str:
            NodeList = [int(i) for i in OID.split(".") if i]
        else :NodeList = OID
        leaf = super().insert(NodeList)
        leaf.leaf_value = value

    def delete(self, OID):
        if type(OID) == str:
            NodeList = [int(i) for i in OID.split(".") if i]
        else :NodeList = OID
        super().delete(NodeList)


    def BFS(self, prefix="", buffer=None, subtree=None):
        if subtree == None :
            subtree = self.root
        if buffer == None:
            buffer = []
        if len(subtree.children) == 0:
            return

        for child in subtree.children:
            if child.word_end:
                buffer.append((prefix+"."+str(child.value),child.leaf_value))
            self.BFS(prefix=prefix+"."+str(child.value), buffer=buffer, subtree = child)

        return buffer

    def snmp_walk(self, OIDkey:str):

        NodeList = [int(i) for i in OIDkey.split(".") if i]
        result , record = self.look_up(NodeList)
        if result:
            subtree_root = record[-1]

            # DFS start from the subtree
            prefix_s = OIDkey
            return self.BFS(prefix=prefix_s, subtree=subtree_root)
        logging.warning("No such OID in tree")
        return None


class Trie(object):
    def __init__(self, word=""):
        self.root = TreeNode('*')
        if(word):
            self.insert(word)

    def print_trie(self, trie=None, depth=0, prefix=""):
        if trie==None :
            trie = self.root
        depth += 1
        if depth <= 1:
            print('\n>> Printing Trie...')
        else:
            prefix += trie.value
            print(depth, prefix)

        if len(trie.children) == 0:
            return

        for node in trie.children:
            self.print_trie(prefix=prefix, trie=node, depth=depth)

        return None

    def insert(self, word):
        logging.info('\n>> Inserting Word "{}"'.format(word))
        node = self.root

        for w in word:
            logging.debug('checking node = {}'.format(node.value))
            for child in node.children:
                if w == child.value:
                    logging.debug('"{}" is found!'.format(w))
                    node = child
                    break
            else:
                # add new node
                logging.debug('letter "{}" not in trie, add!'.format(w))
                new_node = TreeNode(w)
                node.children.append(new_node)
                node = new_node

        # mark the node as ended
        node.word_end = True

        logging.info('word "{}" is added!'.format(word))
        return


    def delete(self, word):
        
        if not word:
            logging.error('\n>> Empty Word intput')
            return
        logging.info('\n>> Deleting Word "{}"'.format(word))

        # 1. check if existed
        logging.debug('>>> Check if the word exists')
        existed, nodes = self.look_up(word)
        if not existed:
            logging.warning('word "{}" not found'.format(word))
            return

        # 2. if existed, start deleted
        logging.debug('>>> Start deleting')
        nodes[-2].children.remove(nodes[-1])

        for i in range(len(nodes)-2, 0, -1):
            # print('pos = {}, word_end? {}'.format(i, nodes[i].word_end))
            if nodes[i].word_end:
                break
            nodes[i-1].children.remove(nodes[i])

        return

# if word exist: return True and its nodes, else: return False and prefix_nodes
    def look_up(self, word: str) -> (bool, list):
        logging.info('\n>> Looking up Word "{}"'.format(word))
        node = self.root
        prefix = ''
        prefix_nodes = [self.root]

        for w in word:
            # print('checking node = {}'.format(w))
            for child in node.children:
                if w == child.value:
                    prefix += w
                    prefix_nodes.append(child)
                    node = child
                    break
            else:
                # word not found
                logging.warning('word "{}" is not found, the nearest prefix is "{}".'.format(word, prefix))

                return False, prefix_nodes

        logging.info('word "{}" is found!'.format(word))
        return True, prefix_nodes

def snmpeater_json(data,D):
    for OID,value in list(data.items()):
        D.insert(OID,value = value)

def snmpeater_rawtext(filename,D):
    with open(filename) as fp:

        line = fp.readline()
        while line:
            
            first_split = line.replace(" ",'').split('=')
            s_OID = first_split[0]
            second_split = first_split[1].split(':')
            s_value = second_split[1]
            D.insert(s_OID,value = s_value)

            line = fp.readline()
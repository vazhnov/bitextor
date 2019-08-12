#!/usr/bin/env python3
import numpy as np
import argparse
import hashlib

from common import MySQL
from helpers import Env

DEBUG = False

######################################################################################
def NumParallelDocs(env, visited):
    ret = 0
    for urlId in visited:
        node = env.nodes[urlId]
        #print("node", node.Debug())

        if node.alignedNode is not None and node.alignedNode.urlId in visited:
            ret += 1

    return ret

######################################################################################
def naive(sqlconn, env, maxDocs):
    todo = []
    todo.append(env.rootNode)

    visited = set()
    langsVisited = {}

    while len(todo) > 0 and len(visited) < maxDocs:
        node = todo.pop()
        #print("node", node.Debug())
        
        if node.urlId not in visited:
            visited.add(node.urlId)
            if node.lang not in langsVisited:
                langsVisited[node.lang] = 0
            langsVisited[node.lang] += 1
            if DEBUG and len(visited) % 40 == 0:
                print("   langsVisited", langsVisited)

            for link in node.links:
                childNode = link.childNode
                #print("   ", childNode.Debug())
                todo.append(childNode)

    numParallelDocs = NumParallelDocs(env, visited)
    print("numParallelDocs", len(visited), numParallelDocs)

######################################################################################
def AddTodo(langsTodo, visited, node, lang):
    if node.urlId in visited:
        return

    if lang not in langsTodo:
        langsTodo[lang] = set()
    langsTodo[lang].add(node)

def PopNode(langsTodo, langsVisited, langs):
    sum = 0
    # any nodes left to do
    for nodes in langsTodo.values():
        sum += len(nodes)
    if sum == 0:
        return None
    del sum

    # sum of all nodes visited
    sumAll = 0
    sumRequired = 0
    for lang, count in langsVisited.items():
        sumAll += count
        if lang in langs:
            sumRequired += count
    #print("langsVisited", sumAll, sumRequired, langsVisited)

    sumRequired += 1
    probs = {}
    for lang in langs:
        if lang in langsVisited:
            count = langsVisited[lang]
        else:
            count = 0
        #print("langsTodo", lang, nodes)
        prob = float(sumRequired - count) / float(sumRequired)
        probs[lang] = prob
    #print("probs", probs)

    nodes = None
    rnd = np.random.rand(1)
    #print("rnd", rnd, len(probs))
    cumm = 0.0
    for lang, prob in probs.items():
        cumm += prob
        #print("prob", prob, cumm)
        if cumm > rnd[0]:
            if lang in langsTodo:
                nodes = langsTodo[lang]
            break
    
    if nodes is not None and len(nodes) > 0:
        node = nodes.pop()
    else:
        node = RandomNode(langsTodo)
    #print("   node", node.Debug())
    return node

def RandomNode(langsTodo):
    while True:
        idx = np.random.randint(0, len(langsTodo))
        langs = list(langsTodo.keys())
        lang = langs[idx]
        nodes = langsTodo[lang]
        #print("idx", idx, len(nodes))
        if len(nodes) > 0:
            return nodes.pop()
    ssfsd
    
######################################################################################
def balanced(sqlconn, env, maxDocs, langs = [1, 4]):
    visited = set()
    langsVisited = {}
    langsTodo = {}
    AddTodo(langsTodo, visited, env.rootNode, env.rootNode.lang)

    node = env.rootNode
    while node is not None and len(visited) < maxDocs:
        if node.urlId not in visited:
            #print("node", node.Debug())
            visited.add(node.urlId)
            if node.lang not in langsVisited:
                langsVisited[node.lang] = 0
            langsVisited[node.lang] += 1
            if DEBUG and len(visited) % 40 == 0:
                print("   langsVisited", langsVisited)
    
            for link in node.links:
                childNode = link.childNode
                #print("   ", childNode.Debug())
                AddTodo(langsTodo, visited, childNode, node.lang)

        node = PopNode(langsTodo, langsVisited, langs)

    numParallelDocs = NumParallelDocs(env, visited)
    print("numParallelDocs", len(visited), numParallelDocs)
        
######################################################################################
def main():
    global DEBUG
    oparser = argparse.ArgumentParser(description="intelligent crawling with q-learning")
    oparser.add_argument("--config-file", dest="configFile", required=True,
                         help="Path to config file (containing MySQL login etc.)")
    options = oparser.parse_args()

    np.random.seed()
    np.set_printoptions(formatter={'float': lambda x: "{0:0.1f}".format(x)}, linewidth=666)

    sqlconn = MySQL(options.configFile)

    #hostName = "http://vade-retro.fr/"
    #hostName = "http://www.buchmann.ch/"
    hostName = "http://www.visitbritain.com/"
    env = Env(sqlconn, hostName)

    for maxDocs in range(50, len(env.nodes), 50):
        print()
        naive(sqlconn, env, maxDocs)   
        balanced(sqlconn, env, maxDocs)
    #naive(sqlconn, env, 600)
    
    DEBUG = True
    balanced(sqlconn, env, 600)
    
main()

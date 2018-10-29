from collections import deque

class TextHistory:
    def __init__(self):
        self._text = ''
        self._version = 0
        self._actions = []
        self._len = 0
    @property
    def text(self):
        return self._text
    
    @property
    def version(self):
        return self._version

    @text.setter
    def text(self, value):
        raise AttributeError

    @version.setter
    def version(self, value):
        raise AttributeError
    
    def check_position(self, pos):
        if pos is None:
            return self._len
        elif pos < 0 or pos > self._len:
            raise ValueError
        else:
            return pos

    def insert(self, text, pos=None, version=None):
        pos = self.check_position(pos)
        if version is None:
            version = self._version + 1
        to_action = InsertAction(pos, text, from_version=self._version, to_version=version)
        return self.action(to_action)

    def replace(self, text, pos=None, version=None):
        pos = self.check_position(pos)
        if version is None:
            version = self._version + 1
        to_action = ReplaceAction(pos, text, from_version=self._version, to_version=version)
        return self.action(to_action)

    
    def delete(self, length, pos=None, version=None):
        if length > len(self._text[pos:pos+length]):
            raise ValueError
        pos = self.check_position(pos)
        if version is None:
            version = self._version + 1
        to_action = DeleteAction(pos, length, from_version=self._version, to_version=version)
        return self.action(to_action)

    def action(self, action:'Action'):
        if action.from_version != self._version and action.from_version == action.to_version:
            raise ValueError
        if action.to_version is None:
            self._version += 1
        else:
            self._version = action.to_version
        self._text = action.apply(self._text)
        self._actions.append(action)
        self._len = len(self._text)
        return self._version

    def get_actions(self, from_version=0, to_version=None):
        if to_version is None:
            to_version = self._version
        if from_version < 0 or from_version > to_version or to_version > self._version:
            raise ValueError
        raw_result = list(filter(lambda action: from_version <= action.from_version and to_version >= action.to_version, self._actions))
        if not raw_result:
            return []
        optimizer = Optimizer(raw_result)
        optimizer.optimize()
        return optimizer.get_optimized()



class Action:
    def __init__(self, pos, from_version, to_version):
        self.pos = pos
        self.from_version = from_version
        self.to_version = to_version
    
    def apply(self, text:str):
        pass


class InsertAction(Action):
    def __init__(self, pos, text, from_version, to_version):
        self.text = text
        super().__init__(pos, from_version, to_version)

    def apply(self, text):
        return text[:self.pos] + self.text + text[self.pos:]


class ReplaceAction(Action):
    def __init__(self, pos, text, from_version, to_version):
        self.text = text
        super().__init__(pos, from_version, to_version)

    def apply(self, text):
        to_position = self.pos + len(self.text)
        return text[:self.pos] + self.text + text[to_position:]


class DeleteAction(Action):
    def __init__(self, pos, length, from_version, to_version):
        self.length = length
        super().__init__(pos, from_version, to_version)

    def apply(self, text):
        return text[:self.pos] + text[self.pos + self.length:]

class Optimizer:
    def __init__(self, actions):
        self.data = deque(actions)
        self.result = []

    def optimize(self):
        deq = deque([self.data.popleft() for i in range(2)])
        while self.data or deq:
            if len(deq) != 2:
                if self.data:
                    deq.append(self.data.popleft())
                else:
                    self.result.append(deq.popleft())
            elif type(deq[0]) == type(deq[1]) and type(deq[0]) is InsertAction:
                deq = self.optimize_insert(deq)
                if len(deq) == 2:
                    self.result.append(deq.popleft())
            else:
                self.result.append(deq.popleft())

    def get_optimized(self):
        return self.result

    def optimize_insert(self, queue):
        action1, action2 = queue
        new_text: str
        if action1.to_version != action2.from_version:
            return queue
        if action1.pos + len(action1.text) == action2.pos:
            new_text = action1.text + action2.text
        elif not action1.pos:
            new_text = action1.text[:action2.pos] + action2.text + action1.text[action2.pos:]      
        else:
            return queue
        new_act = InsertAction(
            pos=action1.pos,
            text=new_text,
            from_version=action1.from_version,
            to_version=action2.to_version
        )
        return deque([new_act])

if __name__ == "__main__":
    a = TextHistory()
    a.insert('asd')
    a.insert('kek', 1)
    a.replace('dea', 2)
    a.delete(2, 3)
    print(a.text)
    print(a.version)
    print(len(a.get_actions()))
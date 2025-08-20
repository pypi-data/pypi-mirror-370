from ..core import asyncio, Callable, pd, np, re, inspect

class BaseSwitch:
    """Clase base con la lógica común para ambos tipos de switch"""
    
    def __init__(self, value, *, match_all=False, debug=False):
        self.value = value
        self.match_all = match_all
        self.debug = debug

    def _match_case(self, key):
        """Lógica común para comparación de casos"""
        try:
            if self.value == key:
                return True

            if isinstance(key, re.Pattern):
                return bool(key.match(str(self.value)))

            if isinstance(key, type):
                return isinstance(self.value, key)

            if isinstance(key, Callable):
                return key(self.value)

            if isinstance(self.value, (pd.Series, pd.DataFrame, np.ndarray)):
                return str(self.value) == str(key)

        except Exception:
            return False

        return False

    def _convert_dict_to_pairs(self, case_dict):
        """Convierte formato de diccionario a pares"""
        pairs = []
        for case in case_dict.get('cases', []):
            pairs.extend([case['case'], case['then']])
        if 'default' in case_dict:
            pairs.extend(['default', case_dict['default']])
        return pairs


class Switch(BaseSwitch):
    """Implementación sincrónica del switch"""
    
    def __call__(self, *cases):
        # Maneja tanto formato de pares como de diccionario
        if len(cases) == 1 and isinstance(cases[0], dict):
            cases = self._convert_dict_to_pairs(cases[0])
        
        if len(cases) % 2 != 0:
            raise ValueError("Cases must be defined in pairs: (condition, action)")

        matched_any = False

        for i in range(0, len(cases), 2):
            condition = cases[i]
            action = cases[i + 1]

            if condition == "default":
                continue

            if self._match_case(condition):
                matched_any = True
                if self.debug:
                    print(f"[Switch] Matched case: {repr(condition)}")

                result = self._run_action(action)
                if not self.match_all:
                    return result

        # Manejo del caso default
        if not matched_any:
            if "default" in cases:
                idx = cases.index("default")
                if self.debug:
                    print("[Switch] Executing default case")
                return self._run_action(cases[idx + 1])
            raise Exception(f"No matching case found for: {repr(self.value)}")

    def _run_action(self, action):
        """Ejecuta una acción sincrónica"""
        return action() if callable(action) else action


class AsyncSwitch(BaseSwitch):
    """Implementación asincrónica del switch"""
    
    async def __call__(self, *cases):
        # Maneja tanto formato de pares como de diccionario
        if len(cases) == 1 and isinstance(cases[0], dict):
            cases = self._convert_dict_to_pairs(cases[0])
        
        if len(cases) % 2 != 0:
            raise ValueError("Cases must be defined in pairs: (condition, action)")

        matched_any = False

        for i in range(0, len(cases), 2):
            condition = cases[i]
            action = cases[i + 1]

            if condition == "default":
                continue

            if self._match_case(condition):
                matched_any = True
                if self.debug:
                    print(f"[AsyncSwitch] Matched case: {repr(condition)}")

                result = await self._run_action(action)
                if not self.match_all:
                    return result

        # Manejo del caso default
        if not matched_any:
            if "default" in cases:
                idx = cases.index("default")
                if self.debug:
                    print("[AsyncSwitch] Executing default case")
                return await self._run_action(cases[idx + 1])
            raise Exception(f"No matching case found for: {repr(self.value)}")

    async def _run_action(self, action):
        """Ejecuta una acción asincrónica"""
        if callable(action):
            if inspect.iscoroutinefunction(action):
                return await action()
            result = action()
            return await result if inspect.isawaitable(result) else result
        return action

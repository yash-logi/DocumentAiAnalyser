"""Unit tests for AST and multi-language code parsing."""

from tools.code_parser import PythonASTParser, JavaScriptTypeScriptParser, CodeParser


def test_python_ast_parser():
    source = """
import os
import sys
from utils.helper import format_text

class DataManager:
    \"\"\"Manages project data.\"\"\"
    def process(self, records):
        return len(records)

async def fetch_feed(url: str):
    return {"url": url}

if __name__ == "__main__":
    print("Running directly")
"""
    res = PythonASTParser.parse("src/manager.py", source)
    assert res.language == "Python"
    assert len(res.classes) == 1
    assert res.classes[0].name == "DataManager"
    assert len(res.functions) == 2
    assert "utils.helper" in res.imports
    assert res.is_entry_point is True


def test_js_ts_parser():
    source = """
import React, { useState } from 'react';
import { Button } from './components/Button';
const axios = require('axios');

export class UserProfile {
    id = 1;
}

export const NavigationBar = (props) => {
    return <div>Nav</div>;
};

export default function App() {
    return <NavigationBar />;
}
"""
    res = JavaScriptTypeScriptParser.parse("app/App.tsx", source)
    assert res.language == "TypeScript"
    assert "./components/Button" in res.imports
    assert "axios" in res.imports
    assert any(c.name == "UserProfile" for c in res.classes)
    assert any(f.name == "NavigationBar" for f in res.functions)

#!/usr/bin/env python3
"""
🔍 Schema Detector Tool for ScriptCraft

Automatically detects and builds database schemas from dataset columns
without reading sensitive data. Supports CSV, Excel, and JSON formats.

Features:
- 📊 Column type inference from headers and sample data
- 🏗️ SQL schema generation (SQLite, SQL Server, PostgreSQL)
- 🔐 Privacy-safe analysis (limited data sampling)
- 📝 Documentation generation
- 🎯 Healthcare/patient data patterns
- 📋 Index and constraint recommendations

Author: ScriptCraft Team
Version: {__version__}
"""

import pandas as pd
import numpy as np
import json
import re
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
import yaml

from scriptcraft.common.core import BaseTool
from scriptcraft.common.logging import setup_logger, log_and_print
from scriptcraft.common.io import ensure_output_dir, get_project_root
from scriptcraft._version import __version__


@dataclass
class ColumnInfo:
    """📊 Information about a dataset column"""
    name: str
    original_name: str
    data_type: str
    sql_type: str
    nullable: bool
    max_length: Optional[int]
    unique_values: int
    sample_values: List[str]
    pattern: Optional[str]
    constraints: List[str]
    is_primary_key: bool
    is_foreign_key: bool
    suggested_indexes: List[str]
    privacy_level: str  # 'public', 'internal', 'sensitive', 'highly_sensitive'


@dataclass
class TableSchema:
    """🏗️ Complete table schema information"""
    name: str
    columns: List[ColumnInfo]
    primary_keys: List[str]
    foreign_keys: Dict[str, str]
    indexes: List[Dict[str, Any]]
    constraints: List[str]
    estimated_rows: int
    table_type: str  # 'fact', 'dimension', 'lookup', 'audit'


class SchemaDetector(BaseTool):
    """🔍 Schema detection tool for datasets"""
    
    def __init__(self):
        super().__init__(
            name="schema_detector", 
            description="🔍 Analyzes datasets and generates database schemas"
        )
        
        # Tool-specific configuration
        self.config = {
            'sample_size': 1000,  # Max rows to analyze for type inference
            'privacy_mode': True,  # Limit data exposure
            'target_database': 'sqlite',  # sqlite, sqlserver, postgresql
            'generate_indexes': True,
            'suggest_constraints': True,
            'output_formats': ['sql', 'json', 'yaml'],
            'healthcare_mode': True,  # Use healthcare-specific patterns
            'naming_convention': 'pascal_case'  # snake_case, pascal_case, camel_case
        }
        
        self.supported_formats = {'.csv', '.xlsx', '.xls', '.json', '.parquet'}
        self.healthcare_patterns = self._init_healthcare_patterns()
        self.data_type_mapping = self._init_data_type_mapping()
        
        self.logger = setup_logger(self.name)
    
    def run(self, input_paths: List[str], output_dir: str = "output", 
            target_database: str = None, privacy_mode: bool = None, **kwargs):
        """
        🚀 Run schema detection on provided datasets
        
        Args:
            input_paths: List of dataset files to analyze
            output_dir: Directory to save generated schemas
            target_database: Target database type (sqlite, sqlserver, postgresql)
            privacy_mode: Enable privacy-safe analysis
            **kwargs: Additional configuration options
        """
        self.log_start()
        
        try:
            # Update configuration with provided parameters
            if target_database:
                self.config['target_database'] = target_database
            if privacy_mode is not None:
                self.config['privacy_mode'] = privacy_mode
            
            # Update with any additional config from kwargs
            for key, value in kwargs.items():
                if key in self.config:
                    self.config[key] = value
            
            log_and_print(f"🔍 Starting schema detection analysis...")
            log_and_print(f"📂 Files to analyze: {len(input_paths)}")
            log_and_print(f"🎯 Target database: {self.config['target_database']}")
            log_and_print(f"🔐 Privacy mode: {'Enabled' if self.config['privacy_mode'] else 'Disabled'}")
            
            # Ensure output directory exists
            output_path = ensure_output_dir(output_dir)
            
            # Analyze datasets
            schemas = self.analyze_datasets(input_paths)
            
            if not schemas:
                log_and_print("❌ No schemas could be detected from the provided files", level="error")
                return False
            
            log_and_print(f"✅ Successfully analyzed {len(schemas)} schema(s)")
            
            # Display results summary
            for schema in schemas:
                log_and_print(f"  🗂️ {schema.name}: {len(schema.columns)} columns, {schema.table_type} table")
                
                # Show privacy summary
                privacy_counts = {}
                for col in schema.columns:
                    privacy_counts[col.privacy_level] = privacy_counts.get(col.privacy_level, 0) + 1
                
                if privacy_counts:
                    privacy_summary = ", ".join([f"{count} {level}" for level, count in privacy_counts.items()])
                    log_and_print(f"    🔐 Privacy levels: {privacy_summary}")
            
            # Save outputs
            self.save_outputs(schemas, output_path)
            
            log_and_print("🎉 Schema detection completed successfully!")
            log_and_print(f"📁 Results saved to: {output_path}")
            
            return True
            
        except Exception as e:
            log_and_print(f"❌ Schema detection failed: {e}", level="error")
            raise
    
    def analyze_datasets(self, input_paths: List[str]) -> List[TableSchema]:
        """🔍 Analyze multiple datasets and return schema information"""
        schemas = []
        
        log_and_print(f"📂 Analyzing {len(input_paths)} dataset(s)")
        
        for path in input_paths:
            path_obj = Path(path)
            
            if not path_obj.exists():
                log_and_print(f"⚠️ File not found: {path}", level="warning")
                continue
            
            if path_obj.suffix.lower() not in self.supported_formats:
                log_and_print(f"⚠️ Unsupported format: {path_obj.suffix}", level="warning")
                continue
            
            try:
                schema = self._analyze_single_dataset(path_obj)
                if schema:
                    schemas.append(schema)
                    log_and_print(f"✅ Successfully analyzed: {path_obj.name}")
            except Exception as e:
                log_and_print(f"❌ Error analyzing {path_obj.name}: {str(e)}", level="error")
        
        return schemas
    
    def _init_healthcare_patterns(self) -> Dict[str, Dict]:
        """🏥 Initialize healthcare-specific column patterns"""
        return {
            'patient_id': {
                'patterns': [r'patient[_\s]*id', r'med[_\s]*id', r'mrn', r'medical[_\s]*record'],
                'sql_type': 'TEXT',
                'constraints': ['UNIQUE', 'NOT NULL'],
                'privacy': 'sensitive',
                'indexes': ['PRIMARY KEY']
            },
            'ssn': {
                'patterns': [r'ssn', r'social[_\s]*security', r'tax[_\s]*id'],
                'sql_type': 'TEXT',
                'constraints': ['UNIQUE'],
                'privacy': 'highly_sensitive',
                'indexes': ['UNIQUE']
            },
            'date_of_birth': {
                'patterns': [r'dob', r'birth[_\s]*date', r'date[_\s]*of[_\s]*birth'],
                'sql_type': 'DATE',
                'constraints': ['NOT NULL'],
                'privacy': 'sensitive',
                'indexes': []
            },
            'diagnosis': {
                'patterns': [r'diagnosis', r'icd[_\s]*code', r'condition'],
                'sql_type': 'TEXT',
                'constraints': [],
                'privacy': 'highly_sensitive',
                'indexes': ['INDEX']
            },
            'medication': {
                'patterns': [r'medication', r'drug', r'prescription', r'ndc'],
                'sql_type': 'TEXT',
                'constraints': [],
                'privacy': 'sensitive',
                'indexes': ['INDEX']
            },
            'provider': {
                'patterns': [r'provider', r'doctor', r'physician', r'npi'],
                'sql_type': 'TEXT',
                'constraints': [],
                'privacy': 'internal',
                'indexes': ['INDEX']
            },
            'visit_date': {
                'patterns': [r'visit[_\s]*date', r'appointment', r'encounter'],
                'sql_type': 'DATE',
                'constraints': [],
                'privacy': 'internal',
                'indexes': ['INDEX']
            },
            'lab_value': {
                'patterns': [r'lab[_\s]*result', r'test[_\s]*value', r'result'],
                'sql_type': 'REAL',
                'constraints': [],
                'privacy': 'sensitive',
                'indexes': []
            }
        }
    
    def _init_data_type_mapping(self) -> Dict[str, Dict[str, str]]:
        """🗂️ Initialize data type mappings for different databases"""
        return {
            'sqlite': {
                'integer': 'INTEGER',
                'float': 'REAL',
                'string': 'TEXT',
                'date': 'TEXT',  # SQLite doesn't have native DATE
                'datetime': 'TEXT',
                'boolean': 'INTEGER',
                'json': 'TEXT'
            },
            'sqlserver': {
                'integer': 'INT',
                'float': 'DECIMAL(18,2)',
                'string': 'NVARCHAR',
                'date': 'DATE',
                'datetime': 'DATETIME2',
                'boolean': 'BIT',
                'json': 'NVARCHAR(MAX)'
            },
            'postgresql': {
                'integer': 'INTEGER',
                'float': 'DECIMAL(10,2)',
                'string': 'VARCHAR',
                'date': 'DATE',
                'datetime': 'TIMESTAMP',
                'boolean': 'BOOLEAN',
                'json': 'JSONB'
            }
        }
    
    def _analyze_single_dataset(self, file_path: Path) -> Optional[TableSchema]:
        """📊 Analyze a single dataset file"""
        log_and_print(f"🔍 Analyzing {file_path.name}...")
        
        # Load data sample for analysis
        df = self._load_data_sample(file_path)
        if df is None or df.empty:
            return None
        
        # Generate table name from filename
        table_name = self._generate_table_name(file_path.stem)
        
        # Analyze each column
        columns = []
        for col_name in df.columns:
            col_info = self._analyze_column(df, col_name)
            columns.append(col_info)
        
        # Determine primary keys and relationships
        primary_keys = self._identify_primary_keys(columns, df)
        foreign_keys = self._identify_foreign_keys(columns)
        
        # Generate indexes and constraints
        indexes = self._generate_indexes(columns, primary_keys)
        constraints = self._generate_constraints(columns)
        
        # Determine table type
        table_type = self._classify_table_type(table_name, columns)
        
        return TableSchema(
            name=table_name,
            columns=columns,
            primary_keys=primary_keys,
            foreign_keys=foreign_keys,
            indexes=indexes,
            constraints=constraints,
            estimated_rows=len(df) if len(df) <= self.config['sample_size'] else -1,
            table_type=table_type
        )
    
    def _load_data_sample(self, file_path: Path) -> Optional[pd.DataFrame]:
        """📥 Load a sample of data for analysis"""
        try:
            sample_size = self.config['sample_size']
            
            if file_path.suffix.lower() == '.csv':
                df = pd.read_csv(file_path, nrows=sample_size)
                log_and_print(f"📋 Found {len(df.columns)} columns in CSV")
                
            elif file_path.suffix.lower() in ['.xlsx', '.xls']:
                df = pd.read_excel(file_path, nrows=sample_size)
                log_and_print(f"📋 Found {len(df.columns)} columns in Excel")
                
            elif file_path.suffix.lower() == '.json':
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                if isinstance(data, list):
                    df = pd.DataFrame(data[:sample_size])
                else:
                    df = pd.DataFrame([data])
                
                log_and_print(f"📋 Found {len(df.columns)} columns in JSON")
                
            elif file_path.suffix.lower() == '.parquet':
                df = pd.read_parquet(file_path, nrows=sample_size)
                log_and_print(f"📋 Found {len(df.columns)} columns in Parquet")
            
            else:
                log_and_print(f"❌ Unsupported file format: {file_path.suffix}", level="error")
                return None
            
            return df
            
        except Exception as e:
            log_and_print(f"❌ Error reading {file_path.name}: {str(e)}", level="error")
            return None
    
    def _analyze_column(self, df: pd.DataFrame, col_name: str) -> ColumnInfo:
        """📊 Analyze a single column to determine its characteristics"""
        series = df[col_name]
        
        # Basic statistics
        non_null_count = series.count()
        total_count = len(series)
        unique_count = series.nunique()
        
        # Determine if nullable
        nullable = non_null_count < total_count
        
        # Get sample values (privacy-safe)
        sample_values = self._get_safe_sample_values(series)
        
        # Infer data type
        data_type, sql_type, max_length = self._infer_data_type(series, col_name)
        
        # Check for healthcare patterns
        privacy_level, pattern, constraints, indexes = self._check_healthcare_patterns(col_name)
        
        # Additional constraints based on data analysis
        additional_constraints = self._analyze_constraints(series, data_type)
        constraints.extend(additional_constraints)
        
        # Determine if this could be a primary or foreign key
        is_primary_key = self._could_be_primary_key(series, col_name)
        is_foreign_key = self._could_be_foreign_key(col_name)
        
        # Generate clean column name
        clean_name = self._clean_column_name(col_name)
        
        return ColumnInfo(
            name=clean_name,
            original_name=col_name,
            data_type=data_type,
            sql_type=sql_type,
            nullable=nullable,
            max_length=max_length,
            unique_values=unique_count,
            sample_values=sample_values,
            pattern=pattern,
            constraints=constraints,
            is_primary_key=is_primary_key,
            is_foreign_key=is_foreign_key,
            suggested_indexes=indexes,
            privacy_level=privacy_level
        )
    
    def _get_safe_sample_values(self, series: pd.Series, max_samples: int = 3) -> List[str]:
        """🔐 Get sample values while respecting privacy"""
        if not self.config['privacy_mode']:
            samples = series.dropna().head(max_samples).astype(str).tolist()
        else:
            samples = []
            for value in series.dropna().head(max_samples):
                if pd.api.types.is_numeric_dtype(type(value)):
                    samples.append("<numeric_value>")
                elif isinstance(value, str):
                    if len(value) <= 3:
                        samples.append("<short_text>")
                    elif len(value) <= 10:
                        samples.append("<medium_text>")
                    else:
                        samples.append("<long_text>")
                else:
                    samples.append(f"<{type(value).__name__}>")
        
        return samples
    
    def _infer_data_type(self, series: pd.Series, col_name: str) -> Tuple[str, str, Optional[int]]:
        """🧠 Infer the data type of a column"""
        clean_series = series.dropna()
        
        if clean_series.empty:
            return 'string', self.data_type_mapping[self.config['target_database']]['string'], None
        
        # Check for integer
        if pd.api.types.is_integer_dtype(clean_series):
            return 'integer', self.data_type_mapping[self.config['target_database']]['integer'], None
        
        # Check for float
        if pd.api.types.is_float_dtype(clean_series):
            return 'float', self.data_type_mapping[self.config['target_database']]['float'], None
        
        # Check for boolean
        if pd.api.types.is_bool_dtype(clean_series):
            return 'boolean', self.data_type_mapping[self.config['target_database']]['boolean'], None
        
        # Check for datetime
        if pd.api.types.is_datetime64_any_dtype(clean_series):
            return 'datetime', self.data_type_mapping[self.config['target_database']]['datetime'], None
        
        # Try to parse as date
        if self._could_be_date(clean_series):
            return 'date', self.data_type_mapping[self.config['target_database']]['date'], None
        
        # Check if it could be numeric (stored as string)
        if self._could_be_numeric(clean_series):
            if self._could_be_integer(clean_series):
                return 'integer', self.data_type_mapping[self.config['target_database']]['integer'], None
            else:
                return 'float', self.data_type_mapping[self.config['target_database']]['float'], None
        
        # Default to string with appropriate length
        max_length = clean_series.astype(str).str.len().max() if not clean_series.empty else 50
        
        # Adjust SQL type based on length and database
        if self.config['target_database'] == 'sqlserver':
            if max_length <= 255:
                sql_type = f"NVARCHAR({min(max_length * 2, 4000)})"
            else:
                sql_type = "NVARCHAR(MAX)"
        elif self.config['target_database'] == 'postgresql':
            if max_length <= 255:
                sql_type = f"VARCHAR({max_length * 2})"
            else:
                sql_type = "TEXT"
        else:  # SQLite
            sql_type = "TEXT"
        
        return 'string', sql_type, max_length
    
    def _could_be_date(self, series: pd.Series) -> bool:
        """📅 Check if a series could contain dates"""
        if len(series) == 0:
            return False
        
        sample = series.head(min(10, len(series)))
        date_count = 0
        
        for value in sample:
            try:
                pd.to_datetime(value)
                date_count += 1
            except:
                continue
        
        return date_count / len(sample) > 0.5
    
    def _could_be_numeric(self, series: pd.Series) -> bool:
        """🔢 Check if string series could be numeric"""
        if len(series) == 0:
            return False
        
        sample = series.head(min(10, len(series)))
        numeric_count = 0
        
        for value in sample:
            try:
                float(str(value))
                numeric_count += 1
            except:
                continue
        
        return numeric_count / len(sample) > 0.8
    
    def _could_be_integer(self, series: pd.Series) -> bool:
        """🔢 Check if numeric series could be integer"""
        if len(series) == 0:
            return False
        
        sample = series.head(min(10, len(series)))
        
        for value in sample:
            try:
                float_val = float(str(value))
                if float_val != int(float_val):
                    return False
            except:
                return False
        
        return True
    
    def _check_healthcare_patterns(self, col_name: str) -> Tuple[str, Optional[str], List[str], List[str]]:
        """🏥 Check column name against healthcare patterns"""
        col_lower = col_name.lower().replace('_', ' ').replace('-', ' ')
        
        for pattern_name, pattern_info in self.healthcare_patterns.items():
            for pattern in pattern_info['patterns']:
                if re.search(pattern, col_lower, re.IGNORECASE):
                    return (
                        pattern_info['privacy'],
                        pattern_name,
                        pattern_info['constraints'].copy(),
                        pattern_info['indexes'].copy()
                    )
        
        # Default classification
        if any(term in col_lower for term in ['id', 'key', 'number']):
            return 'internal', None, [], ['INDEX']
        elif any(term in col_lower for term in ['name', 'address', 'phone', 'email']):
            return 'sensitive', None, [], []
        else:
            return 'public', None, [], []
    
    def _analyze_constraints(self, series: pd.Series, data_type: str) -> List[str]:
        """🔒 Analyze data to suggest constraints"""
        constraints = []
        
        # Check for NOT NULL constraint
        if series.count() == len(series):
            constraints.append('NOT NULL')
        
        # Check for UNIQUE constraint
        if series.nunique() == series.count():
            constraints.append('UNIQUE')
        
        # Check for CHECK constraints based on data type
        if data_type in ['integer', 'float']:
            min_val = series.min()
            if min_val >= 0:
                constraints.append(f'CHECK ({self._clean_column_name(series.name)} >= 0)')
        
        return constraints
    
    def _could_be_primary_key(self, series: pd.Series, col_name: str) -> bool:
        """🔑 Determine if column could be a primary key"""
        col_lower = col_name.lower()
        
        if any(pattern in col_lower for pattern in ['id', 'key', 'number']) and col_lower.endswith('id'):
            if series.nunique() == series.count() and series.count() == len(series):
                return True
        
        return False
    
    def _could_be_foreign_key(self, col_name: str) -> bool:
        """🔗 Determine if column could be a foreign key"""
        col_lower = col_name.lower()
        fk_patterns = ['patient_id', 'provider_id', 'user_id', 'visit_id', 'appointment_id']
        return any(pattern in col_lower for pattern in fk_patterns)
    
    def _clean_column_name(self, col_name: str) -> str:
        """🧹 Clean and standardize column names"""
        clean_name = re.sub(r'[^\w\s]', '', col_name)
        
        if self.config['naming_convention'] == 'snake_case':
            clean_name = re.sub(r'\s+', '_', clean_name.lower())
        elif self.config['naming_convention'] == 'pascal_case':
            clean_name = ''.join(word.capitalize() for word in clean_name.split())
        elif self.config['naming_convention'] == 'camel_case':
            words = clean_name.split()
            clean_name = words[0].lower() + ''.join(word.capitalize() for word in words[1:])
        
        return clean_name
    
    def _generate_table_name(self, filename: str) -> str:
        """🏷️ Generate appropriate table name from filename"""
        name = re.sub(r'(_data|_dataset|_table|_export)', '', filename.lower())
        
        if self.config['naming_convention'] == 'pascal_case':
            name = ''.join(word.capitalize() for word in name.split('_'))
        
        return name
    
    def _identify_primary_keys(self, columns: List[ColumnInfo], df: pd.DataFrame) -> List[str]:
        """🔑 Identify primary key columns"""
        primary_keys = []
        
        for col in columns:
            if col.is_primary_key:
                primary_keys.append(col.name)
        
        if not primary_keys:
            for col in columns:
                if 'id' in col.name.lower() and 'UNIQUE' in col.constraints:
                    primary_keys.append(col.name)
                    break
        
        return primary_keys
    
    def _identify_foreign_keys(self, columns: List[ColumnInfo]) -> Dict[str, str]:
        """🔗 Identify foreign key relationships"""
        foreign_keys = {}
        
        for col in columns:
            if col.is_foreign_key:
                if 'patient_id' in col.name.lower():
                    foreign_keys[col.name] = 'Patients(PatientId)'
                elif 'provider_id' in col.name.lower():
                    foreign_keys[col.name] = 'Providers(ProviderId)'
                elif 'user_id' in col.name.lower():
                    foreign_keys[col.name] = 'Users(UserId)'
        
        return foreign_keys
    
    def _generate_indexes(self, columns: List[ColumnInfo], primary_keys: List[str]) -> List[Dict[str, Any]]:
        """📋 Generate recommended indexes"""
        indexes = []
        
        if primary_keys:
            indexes.append({
                'name': f'PK_{primary_keys[0]}' if len(primary_keys) == 1 else 'PK_Composite',
                'type': 'PRIMARY KEY',
                'columns': primary_keys,
                'unique': True
            })
        
        for col in columns:
            if 'UNIQUE' in col.constraints and col.name not in primary_keys:
                indexes.append({
                    'name': f'UQ_{col.name}',
                    'type': 'UNIQUE',
                    'columns': [col.name],
                    'unique': True
                })
        
        for col in columns:
            if col.is_foreign_key or 'INDEX' in col.suggested_indexes:
                indexes.append({
                    'name': f'IX_{col.name}',
                    'type': 'INDEX',
                    'columns': [col.name],
                    'unique': False
                })
        
        return indexes
    
    def _generate_constraints(self, columns: List[ColumnInfo]) -> List[str]:
        """🔒 Generate table-level constraints"""
        constraints = []
        
        for col in columns:
            for constraint in col.constraints:
                if constraint.startswith('CHECK'):
                    constraints.append(constraint)
        
        return constraints
    
    def _classify_table_type(self, table_name: str, columns: List[ColumnInfo]) -> str:
        """🏷️ Classify the type of table"""
        name_lower = table_name.lower()
        
        if any(term in name_lower for term in ['audit', 'log', 'history']):
            return 'audit'
        
        if any(term in name_lower for term in ['lookup', 'reference', 'code', 'type']):
            return 'lookup'
        
        numeric_cols = sum(1 for col in columns if col.data_type in ['integer', 'float'])
        if numeric_cols / len(columns) > 0.4:
            return 'fact'
        
        return 'dimension'
    
    def generate_sql_schema(self, schemas: List[TableSchema]) -> str:
        """🏗️ Generate complete SQL schema script"""
        sql_parts = []
        
        sql_parts.append(f"""
-- 🗄️ Auto-Generated Database Schema
-- Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
-- Target Database: {self.config['target_database'].upper()}
-- Total Tables: {len(schemas)}
--
-- 🔍 Schema Detection Tool v{__version__}
-- Generated from dataset analysis with privacy protection
""")
        
        for schema in schemas:
            sql_parts.append(self._generate_table_sql(schema))
        
        if self.config['generate_indexes']:
            sql_parts.append("\n-- 📋 Indexes for Performance")
            for schema in schemas:
                sql_parts.append(self._generate_indexes_sql(schema))
        
        return '\n'.join(sql_parts)
    
    def _generate_table_sql(self, schema: TableSchema) -> str:
        """🏗️ Generate SQL for a single table"""
        lines = []
        
        lines.append(f"\n-- {schema.name} ({schema.table_type.title()} Table)")
        if schema.estimated_rows > 0:
            lines.append(f"-- Estimated rows: {schema.estimated_rows:,}")
        
        lines.append(f"CREATE TABLE {schema.name} (")
        
        column_lines = []
        for col in schema.columns:
            col_def = self._format_column_definition(col)
            column_lines.append(f"    {col_def}")
        
        if schema.primary_keys:
            if len(schema.primary_keys) == 1:
                for i, line in enumerate(column_lines):
                    if schema.primary_keys[0] in line:
                        column_lines[i] = line.replace(',', ' PRIMARY KEY,')
                        break
            else:
                pk_constraint = f"    PRIMARY KEY ({', '.join(schema.primary_keys)})"
                column_lines.append(pk_constraint)
        
        for fk_col, fk_ref in schema.foreign_keys.items():
            fk_constraint = f"    FOREIGN KEY ({fk_col}) REFERENCES {fk_ref}"
            column_lines.append(fk_constraint)
        
        for constraint in schema.constraints:
            column_lines.append(f"    {constraint}")
        
        lines.append(',\n'.join(column_lines))
        lines.append(");")
        
        return '\n'.join(lines)
    
    def _format_column_definition(self, col: ColumnInfo) -> str:
        """📝 Format a single column definition"""
        parts = [col.name, col.sql_type]
        
        for constraint in col.constraints:
            if constraint not in ['PRIMARY KEY', 'UNIQUE']:
                parts.append(constraint)
        
        definition = ' '.join(parts) + ','
        
        if col.original_name != col.name or col.privacy_level != 'public':
            comment_parts = []
            if col.original_name != col.name:
                comment_parts.append(f"Originally: {col.original_name}")
            if col.privacy_level != 'public':
                comment_parts.append(f"Privacy: {col.privacy_level}")
            
            definition += f"  -- {', '.join(comment_parts)}"
        
        return definition
    
    def _generate_indexes_sql(self, schema: TableSchema) -> str:
        """📋 Generate index creation SQL"""
        lines = []
        
        for index in schema.indexes:
            if index['type'] == 'PRIMARY KEY':
                continue
            
            index_name = f"{index['name']}_{schema.name}"
            columns = ', '.join(index['columns'])
            
            if index['type'] == 'UNIQUE':
                lines.append(f"CREATE UNIQUE INDEX {index_name} ON {schema.name} ({columns});")
            else:
                lines.append(f"CREATE INDEX {index_name} ON {schema.name} ({columns});")
        
        return '\n'.join(lines)
    
    def generate_documentation(self, schemas: List[TableSchema]) -> str:
        """📚 Generate documentation for the detected schema"""
        doc_parts = []
        
        doc_parts.append(f"""
# 📊 Dataset Schema Analysis Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Tool**: Schema Detection Tool v{__version__}  
**Database Target**: {self.config['target_database'].upper()}  
**Tables Analyzed**: {len(schemas)}

## 🔍 Analysis Summary

| Metric | Value |
|--------|-------|
| Total Tables | {len(schemas)} |
| Total Columns | {sum(len(s.columns) for s in schemas)} |
| Primary Keys Detected | {sum(1 for s in schemas if s.primary_keys)} |
| Foreign Keys Detected | {sum(len(s.foreign_keys) for s in schemas)} |
| Highly Sensitive Columns | {sum(1 for s in schemas for c in s.columns if c.privacy_level == 'highly_sensitive')} |
| Sensitive Columns | {sum(1 for s in schemas for c in s.columns if c.privacy_level == 'sensitive')} |

""")
        
        doc_parts.append("## 🏗️ Table Schemas\n")
        
        for schema in schemas:
            doc_parts.append(f"### {schema.name}\n")
            doc_parts.append(f"**Type**: {schema.table_type.title()}")
            if schema.estimated_rows > 0:
                doc_parts.append(f"  \n**Estimated Rows**: {schema.estimated_rows:,}")
            doc_parts.append("\n")
            
            doc_parts.append("| Column | Type | Nullable | Privacy | Constraints |")
            doc_parts.append("|--------|------|----------|---------|-------------|")
            
            for col in schema.columns:
                nullable = "✅" if col.nullable else "❌"
                privacy_emoji = {
                    'public': '🟢',
                    'internal': '🟡',
                    'sensitive': '🟠',
                    'highly_sensitive': '🔴'
                }.get(col.privacy_level, '⚪')
                
                constraints = ', '.join(col.constraints) if col.constraints else '-'
                
                doc_parts.append(f"| {col.name} | {col.data_type} | {nullable} | {privacy_emoji} {col.privacy_level} | {constraints} |")
            
            doc_parts.append("\n")
        
        doc_parts.append("## 🔐 Privacy & Security Recommendations\n")
        
        for schema in schemas:
            sensitive_cols = [c for c in schema.columns if c.privacy_level in ['sensitive', 'highly_sensitive']]
            if sensitive_cols:
                doc_parts.append(f"### {schema.name}")
                for col in sensitive_cols:
                    if col.privacy_level == 'highly_sensitive':
                        doc_parts.append(f"- **{col.name}**: Requires encryption at rest and in transit")
                    else:
                        doc_parts.append(f"- **{col.name}**: Requires access logging and controlled access")
                doc_parts.append("")
        
        return '\n'.join(doc_parts)
    
    def save_outputs(self, schemas: List[TableSchema], output_dir: Path):
        """💾 Save all generated outputs"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save SQL schema
        if 'sql' in self.config['output_formats']:
            sql_content = self.generate_sql_schema(schemas)
            sql_file = output_dir / f'detected_schema_{timestamp}.sql'
            with open(sql_file, 'w', encoding='utf-8') as f:
                f.write(sql_content)
            log_and_print(f"💾 SQL schema saved: {sql_file}")
        
        # Save JSON schema
        if 'json' in self.config['output_formats']:
            json_data = {
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'tool_version': __version__,
                    'target_database': self.config['target_database']
                },
                'schemas': [self._schema_to_dict(schema) for schema in schemas]
            }
            json_file = output_dir / f'detected_schema_{timestamp}.json'
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2)
            log_and_print(f"💾 JSON schema saved: {json_file}")
        
        # Save YAML schema
        if 'yaml' in self.config['output_formats']:
            yaml_data = {
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'tool_version': __version__,
                    'target_database': self.config['target_database']
                },
                'schemas': [self._schema_to_dict(schema) for schema in schemas]
            }
            yaml_file = output_dir / f'detected_schema_{timestamp}.yaml'
            with open(yaml_file, 'w', encoding='utf-8') as f:
                yaml.dump(yaml_data, f, default_flow_style=False, sort_keys=False)
            log_and_print(f"💾 YAML schema saved: {yaml_file}")
        
        # Save documentation
        doc_content = self.generate_documentation(schemas)
        doc_file = output_dir / f'schema_analysis_report_{timestamp}.md'
        with open(doc_file, 'w', encoding='utf-8') as f:
            f.write(doc_content)
        log_and_print(f"📚 Documentation saved: {doc_file}")
    
    def _schema_to_dict(self, schema: TableSchema) -> Dict:
        """🔄 Convert TableSchema to dictionary for JSON/YAML export"""
        return {
            'name': schema.name,
            'type': schema.table_type,
            'estimated_rows': schema.estimated_rows,
            'columns': [
                {
                    'name': col.name,
                    'original_name': col.original_name,
                    'data_type': col.data_type,
                    'sql_type': col.sql_type,
                    'nullable': bool(col.nullable),
                    'max_length': col.max_length,
                    'unique_values': int(col.unique_values) if col.unique_values is not None else None,
                    'privacy_level': col.privacy_level,
                    'constraints': col.constraints,
                    'is_primary_key': bool(col.is_primary_key),
                    'is_foreign_key': bool(col.is_foreign_key),
                    'sample_values': col.sample_values
                }
                for col in schema.columns
            ],
            'primary_keys': schema.primary_keys,
            'foreign_keys': schema.foreign_keys,
            'indexes': schema.indexes,
            'constraints': schema.constraints
        }


# Tool class is available for import
# Instantiate when needed: tool = SchemaDetector() 
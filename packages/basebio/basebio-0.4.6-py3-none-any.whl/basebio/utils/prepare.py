#!/usr/bin/env python3
import os, re, glob, shutil, yaml
from pathlib import Path
from datetime import datetime

class Prepare(object):
    def __init__(self, input_dir, output_dir, ref_dir, species, prefix, control_names=None, pipeline=None, renames=None, customer=None, detail=None, support=None):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.ref_dir = ref_dir
        self.species = species
        self.prefix = prefix
        self.control_names = control_names
        self.pipeline = pipeline
        self.renames = renames
        self.customer = customer
        self.detail = detail
        self.support = support
        self.config_file = os.path.join(input_dir, "config.yaml")
        self.species_ref = {
            "human": "hg38",
            "mouse": "mm10",
            "rat": "rat7",
            "other": "other"
        }
        self.reference = os.path.join(ref_dir, self.species_ref[self.species])
        self.ref_link = os.path.join(output_dir, "reference")
        self.tmp = {}

    def clean_read1_name(self, r1name):
        pattern = re.compile(r'[._]?[R_]1.*$')
        return re.sub(pattern, '', r1name)

    def generate_config(self):
        """
        Generate YAML format configuration file
        """
        # Prepare YAML data structure
        config = {
            "metadata": {
                "creation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "pipeline": self.pipeline
            },
            "input_dir": self.input_dir,
            "output_dir": self.output_dir,
            "ref_dir": self.ref_dir,
            "species": self.species,
            "prefix": self.prefix,
            "support": self.support,
            "customer": self.customer,
            "detail": self.detail,
            "samples": {},
        }
        if self.renames is None:
            file_list = glob.glob(os.path.join(self.input_dir, "**", "*[R_]1.[cf]*q.gz"), recursive=True)
            for file_path in file_list:
                rawname_r1 = os.path.basename(file_path)
                rawname = self.clean_read1_name(rawname_r1)
                rename = rawname
                if self.tmp.get(rawname_r1, None) is None:
                    self.tmp[rawname_r1] = [rename, rawname]
                
        else:
            for raw in self.renames.split(','):
                rawname = raw.split(':')[0]
                raw_path = glob.glob(os.path.join(self.input_dir, "**", f"{rawname}*[R_]1.[cf]*q.gz"), recursive=True)
                if raw_path:
                    rawname_r1 = os.path.basename(raw_path[0])
                else:
                    print(f"\033[1;31mRaw file not found: {rawname}\033[0m")
                    return
                rename = raw.split(':')[1]
                if self.tmp.get(rawname_r1, None) is None:
                    self.tmp[rawname_r1] = [rename, rawname]
        
        control_list = set(self.control_names.split(',')) if self.control_names else []
        for rawname_r1 in self.tmp.keys():
            # Determine R2 file name
            if "_1" in rawname_r1:
                rawname_r2 = rawname_r1.replace("_1", "_2", 1)
            else:
                rawname_r2 = rawname_r1.replace("R1", "R2", 1)
            
            # Extract sample name prefix
            sample_rename = self.tmp[rawname_r1][0]
            sample_rawname = self.tmp[rawname_r1][1]
            
            # Add to configuration
            
            if sample_rename in control_list or sample_rawname in control_list:
                config["samples"][sample_rename] = {
                    "R1": rawname_r1,
                    "R2": rawname_r2,
                    "group": "Control",
                }
            else:
                config["samples"][sample_rename] = {
                    "R1": rawname_r1,
                    "R2": rawname_r2,
                    "group": "Treatment",
                }
        
        # Write YAML file
        with open(self.config_file, "w") as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)

    def init_structure(self):
        try:
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)
            else:
                print(f"\033[1;31mOutput directory already exists: {self.output_dir}\033[0m")
                return
            if not os.path.exists(self.config_file):
                self.generate_config()
            with open(self.config_file, "r") as f:
                config = yaml.safe_load(f)
        except Exception as e:
            print(f"\033[1;31mError loading YAML config: {e}\033[0m")
            return
        
        # 验证配置文件结构
        if "samples" not in config:
            print("\033[1;31mInvalid config: missing 'samples' section\033[0m")
            return
        
        if self.species not in self.species_ref:
            print(f"Sorry, you can choose species in {list(self.species_ref.keys())}, "
                "and other species that we do not build.")
            return
        
        # 创建输出目录结构
        Path(os.path.join(self.output_dir, "tmp")).mkdir(parents=True, exist_ok=True)
        Path(os.path.join(self.output_dir, "log")).mkdir(parents=True, exist_ok=True)
        Path(os.path.join(self.output_dir, "config")).mkdir(parents=True, exist_ok=True)
        
        # 创建参考基因组的符号链接
        if not os.path.exists(self.ref_link):
            os.symlink(self.reference, self.ref_link)
        
        # 准备样本列表
        sample_names = []
        
        # 处理每个样本
        for sample_id, sample_info in config["samples"].items():
            sample_r1 = sample_info["R1"]
            sample_r2 = sample_info["R2"]
            
            # 创建新的样本名: group_sample_id
            new_sample_name = sample_id
            sample_names.append(new_sample_name)
            
            # 创建样本目录
            sample_dir = os.path.join(self.output_dir, "input", new_sample_name)
            Path(sample_dir).mkdir(parents=True, exist_ok=True)
            
            # 查找R1文件
            r1_files = glob.glob(os.path.join(self.input_dir, "**", sample_r1), recursive=True)
            # 查找R2文件
            r2_files = glob.glob(os.path.join(self.input_dir, "**", sample_r2), recursive=True)
            
            # 输出文件路径
            r1_output = os.path.join(sample_dir, f"{new_sample_name}_R1.fastq.gz")
            r2_output = os.path.join(sample_dir, f"{new_sample_name}_R2.fastq.gz")
            
            # 处理找到的文件
            if len(r1_files) > 1 or len(r2_files) > 1:
                # 合并R1文件
                with open(r1_output, "wb") as outfile:
                    for fname in r1_files:
                        with open(fname, "rb") as infile:
                            shutil.copyfileobj(infile, outfile)
                
                # 合并R2文件
                with open(r2_output, "wb") as outfile:
                    for fname in r2_files:
                        with open(fname, "rb") as infile:
                            shutil.copyfileobj(infile, outfile)
            else:
                # 只找到一个文件，创建符号链接
                r1_file = r1_files[0] if r1_files else None
                r2_file = r2_files[0] if r2_files else None
                
                if r1_file and os.path.exists(r1_file):
                    if not os.path.exists(r1_output):
                        os.symlink(r1_file, r1_output)
                else:
                    print(f"\033[1;31mR1 file not found: {sample_r1}\033[0m")
                
                if r2_file and os.path.exists(r2_file):
                    if not os.path.exists(r2_output):
                        os.symlink(r2_file, r2_output)
                else:
                    print(f"\033[1;31mR2 file not found: {sample_r2}\033[0m")
        
        # 写入样本列表文件
        with open(os.path.join(self.output_dir, "config", "sample"), "w") as f:
            for name in sample_names:
                f.write(f"{name}\n")
        
        # 保存配置文件副本
        shutil.copy(self.config_file, os.path.join(self.output_dir, "config", "config.yaml"))
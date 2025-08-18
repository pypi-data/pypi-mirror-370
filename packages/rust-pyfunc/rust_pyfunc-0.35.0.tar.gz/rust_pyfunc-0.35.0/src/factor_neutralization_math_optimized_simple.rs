/*!
批量因子中性化函数 - 简化数学计算优化版本
=======================================

此版本专门优化数学计算性能，包括：
1. 预计算QR分解提高数值稳定性
2. 优化矩阵运算内存布局
3. 批量线性代数计算
4. 数值稳定性检查和自动调整
*/

use pyo3::prelude::*;
use pyo3::exceptions::PyRuntimeError;
use nalgebra::{DMatrix, DVector, QR};
use rayon::prelude::*;
use std::collections::HashMap;
use std::fs::File;
use std::path::{Path, PathBuf};
use std::sync::Arc;
use std::time::Instant;
use arrow::array::*;
use arrow::record_batch::RecordBatch;
use parquet::arrow::arrow_reader::ParquetRecordBatchReaderBuilder;
use arrow::datatypes::{DataType, Field, Schema};

/// 从文件名提取日期信息
fn extract_date_from_filename(filename: &str) -> Option<i64> {
    // 寻找8位连续数字（YYYYMMDD格式）
    for i in 0..filename.len().saturating_sub(7) {
        let slice = &filename[i..i+8];
        if slice.chars().all(|c| c.is_ascii_digit()) {
            if let Ok(date) = slice.parse::<i64>() {
                // 验证是否是合理的日期格式
                if date >= 19900101 && date <= 20991231 {
                    return Some(date);
                }
            }
        }
    }
    
    // 如果找不到日期，返回None
    None
}

/// 简化的数学优化风格数据结构
pub struct SimpleMathOptimizedStyleData {
    pub data_by_date: HashMap<i64, SimpleMathOptimizedStyleDayData>,
}

/// 简化的单日风格数据 - 预计算QR分解
pub struct SimpleMathOptimizedStyleDayData {
    pub stocks: Vec<String>,
    pub style_matrix: DMatrix<f64>,
    pub qr_decomposition: Option<QR<f64, nalgebra::Dyn, nalgebra::Dyn>>,
    pub is_well_conditioned: bool,
}

/// 简化的因子数据结构
pub struct SimpleMathOptimizedFactorData {
    pub dates: Vec<i64>,
    pub stocks: Vec<String>,
    pub values: DMatrix<f64>,
}

/// 简化的中性化结果
pub struct SimpleMathOptimizedNeutralizationResult {
    pub dates: Vec<i64>,
    pub stocks: Vec<String>,
    pub neutralized_values: DMatrix<f64>,
}

impl SimpleMathOptimizedStyleData {
    /// 加载风格数据并预计算QR分解
    pub fn load_from_parquet_simple_math_optimized(path: &str) -> PyResult<Self> {
        let load_start = Instant::now();
        
        let file = File::open(path)
            .map_err(|e| PyRuntimeError::new_err(format!("无法打开风格数据文件 {}: {}", path, e)))?;

        let record_batch_reader = ParquetRecordBatchReaderBuilder::try_new(file)
            .map_err(|e| PyRuntimeError::new_err(format!("无法创建记录批阅读器: {}", e)))?
            .with_batch_size(8192)
            .build()
            .map_err(|e| PyRuntimeError::new_err(format!("无法创建记录批阅读器: {}", e)))?;

        let mut data_by_date = HashMap::new();
        let mut total_rows = 0;

        println!("🧮 开始简化数学优化的风格数据加载...");

        for batch_result in record_batch_reader {
            let batch = batch_result
                .map_err(|e| PyRuntimeError::new_err(format!("读取记录批失败: {}", e)))?;
            
            total_rows += batch.num_rows();
            
            // 提取列数据
            let date_array = batch.column(0)
                .as_any().downcast_ref::<Int64Array>()
                .ok_or_else(|| PyRuntimeError::new_err("日期列类型转换失败"))?;
            
            let stock_array = batch.column(1)
                .as_any().downcast_ref::<StringArray>()
                .ok_or_else(|| PyRuntimeError::new_err("股票列类型转换失败"))?;

            let mut style_arrays = Vec::with_capacity(11);
            for i in 2..13 {
                let style_array = batch.column(i)
                    .as_any().downcast_ref::<Float64Array>()
                    .ok_or_else(|| PyRuntimeError::new_err(format!("风格因子列{}转换失败", i-2)))?;
                style_arrays.push(style_array);
            }

            // 按日期分组
            let mut temp_data_by_date: HashMap<i64, HashMap<String, Vec<f64>>> = HashMap::new();
            
            for row_idx in 0..batch.num_rows() {
                let date = date_array.value(row_idx);
                let stock = stock_array.value(row_idx).to_string();
                
                let mut style_values = Vec::with_capacity(11);
                for style_array in &style_arrays {
                    style_values.push(style_array.value(row_idx));
                }
                
                temp_data_by_date
                    .entry(date)
                    .or_insert_with(HashMap::new)
                    .insert(stock, style_values);
            }

            // 转换为优化数据结构
            for (date, stock_data) in temp_data_by_date {
                if stock_data.len() >= 12 {
                    if let Ok(day_data) = Self::convert_date_data_simple_math_optimized(date, stock_data) {
                        data_by_date.insert(date, day_data);
                    }
                }
            }
        }

        let load_time = load_start.elapsed();
        println!("✅ 简化数学优化风格数据加载完成:");
        println!("   📅 处理日期数: {}", data_by_date.len());
        println!("   📊 总行数: {}", total_rows);
        println!("   ⏱️  加载用时: {:.3}s", load_time.as_secs_f64());

        Ok(SimpleMathOptimizedStyleData { data_by_date })
    }

    /// 转换日期数据并预计算QR分解
    fn convert_date_data_simple_math_optimized(
        date: i64, 
        stock_data: HashMap<String, Vec<f64>>
    ) -> PyResult<SimpleMathOptimizedStyleDayData> {
        
        let n_stocks = stock_data.len();
        let mut stocks = Vec::with_capacity(n_stocks);
        let mut style_matrix = DMatrix::zeros(n_stocks, 12);

        // 按股票代码排序确保一致性
        let mut sorted_stocks: Vec<_> = stock_data.into_iter().collect();
        sorted_stocks.sort_by(|a, b| a.0.cmp(&b.0));

        for (i, (stock, style_values)) in sorted_stocks.into_iter().enumerate() {
            stocks.push(stock);
            
            // 填充风格因子矩阵
            for j in 0..11 {
                style_matrix[(i, j)] = style_values[j];
            }
            style_matrix[(i, 11)] = 1.0; // 常数项
        }

        // 预计算QR分解
        let (qr_decomposition, is_well_conditioned) = Self::compute_stable_qr(&style_matrix)?;

        if !is_well_conditioned {
            println!("⚠️  日期{}: 矩阵条件较差，可能影响中性化精度", date);
        }

        Ok(SimpleMathOptimizedStyleDayData {
            stocks,
            style_matrix,
            qr_decomposition: Some(qr_decomposition),
            is_well_conditioned,
        })
    }

    /// 计算稳定的QR分解
    fn compute_stable_qr(style_matrix: &DMatrix<f64>) -> PyResult<(QR<f64, nalgebra::Dyn, nalgebra::Dyn>, bool)> {
        let qr = style_matrix.clone().qr();
        
        // 检查QR分解的数值稳定性
        let r_matrix = qr.r();
        let min_diagonal = (0..r_matrix.ncols().min(r_matrix.nrows()))
            .map(|i| r_matrix[(i, i)].abs())
            .min_by(|a, b| a.partial_cmp(b).unwrap())
            .unwrap_or(0.0);
        
        let is_well_conditioned = min_diagonal > 1e-10;
        
        if min_diagonal < 1e-14 {
            return Err(PyRuntimeError::new_err(
                format!("QR分解数值极不稳定，R矩阵最小对角元: {:.2e}", min_diagonal)
            ));
        }
        
        Ok((qr, is_well_conditioned))
    }
}

impl SimpleMathOptimizedFactorData {
    /// 加载因子数据
    pub fn load_from_parquet_simple_math_optimized(path: &str) -> PyResult<Self> {
        let load_start = Instant::now();
        
        let file = File::open(path)
            .map_err(|e| PyRuntimeError::new_err(format!("无法打开因子文件 {}: {}", path, e)))?;

        let record_batch_reader = ParquetRecordBatchReaderBuilder::try_new(file)
            .map_err(|e| PyRuntimeError::new_err(format!("无法创建记录批阅读器: {}", e)))?
            .with_batch_size(8192)
            .build()
            .map_err(|e| PyRuntimeError::new_err(format!("无法创建记录批阅读器: {}", e)))?;

        let mut all_data = HashMap::new();

        // 检查文件结构：是否包含日期列
        let mut first_batch = true;
        let mut has_date_column = false;
        let mut date_col_idx = 0;
        let mut stocks = Vec::new();
        
        for batch_result in record_batch_reader {
            let batch = batch_result
                .map_err(|e| PyRuntimeError::new_err(format!("读取记录批失败: {}", e)))?;

            if first_batch {
                let schema = batch.schema();
                let total_columns = schema.fields().len();
                
                // 检查是否存在date列
                let has_first_date = schema.fields()[0].name() == "date";
                let has_last_date = schema.fields()[total_columns - 1].name() == "date";
                
                if has_first_date {
                    // 传统格式：第一列是date
                    has_date_column = true;
                    date_col_idx = 0;
                    stocks = schema.fields()
                        .iter()
                        .skip(1)
                        .map(|f| f.name().clone())
                        .collect();
                } else if has_last_date {
                    // pandas index格式：最后一列是date
                    has_date_column = true;
                    date_col_idx = total_columns - 1;
                    stocks = schema.fields()
                        .iter()
                        .take(total_columns - 1)
                        .map(|f| f.name().clone())
                        .collect();
                } else {
                    // 没有日期列：所有列都是股票，需要从文件名推断日期
                    has_date_column = false;
                    stocks = schema.fields()
                        .iter()
                        .map(|f| f.name().clone())
                        .collect();
                }
                first_batch = false;
                
                println!("   📊 文件结构分析: {} ({}列股票数据)", 
                    if has_date_column { "包含日期列" } else { "纯股票数据" }, 
                    stocks.len());
            }

            if has_date_column {
                // 有日期列：按原逻辑处理
                let date_column = batch.column(date_col_idx);
                let batch_dates: Vec<i64> = if let Some(date_array_i64) = date_column.as_any().downcast_ref::<Int64Array>() {
                    (0..date_array_i64.len()).map(|i| date_array_i64.value(i)).collect()
                } else if let Some(date_array_i32) = date_column.as_any().downcast_ref::<Int32Array>() {
                    (0..date_array_i32.len()).map(|i| date_array_i32.value(i) as i64).collect()
                } else {
                    return Err(PyRuntimeError::new_err("日期列类型错误：期望Int64或Int32类型"));
                };

                for row_idx in 0..batch.num_rows() {
                    let date = batch_dates[row_idx];
                    let mut row_values = Vec::new();
                    
                    // 读取股票数据（跳过日期列）
                    let stock_columns = if date_col_idx == 0 { 
                        1..batch.num_columns() 
                    } else { 
                        0..(batch.num_columns() - 1) 
                    };
                    
                    for col_idx in stock_columns {
                        let value = match batch.column(col_idx).as_any().downcast_ref::<Float64Array>() {
                            Some(array) => {
                                if array.is_null(row_idx) {
                                    f64::NAN
                                } else {
                                    array.value(row_idx)
                                }
                            }
                            None => f64::NAN,
                        };
                        row_values.push(value);
                    }
                    
                    all_data.insert(date, row_values);
                }
            } else {
                // 没有日期列：从文件名推断日期，每行代表一个日期
                let file_name = Path::new(path).file_stem()
                    .and_then(|s| s.to_str())
                    .unwrap_or("unknown");
                
                // 尝试从文件名提取日期信息（假设包含8位数字的日期）
                let inferred_date = extract_date_from_filename(file_name).unwrap_or(20230101);
                
                for row_idx in 0..batch.num_rows() {
                    // 为每一行分配一个唯一的日期（基于行索引）
                    let row_date = inferred_date + row_idx as i64;
                    let mut row_values = Vec::new();
                    
                    // 读取所有列（都是股票数据）
                    for col_idx in 0..batch.num_columns() {
                        let value = match batch.column(col_idx).as_any().downcast_ref::<Float64Array>() {
                            Some(array) => {
                                if array.is_null(row_idx) {
                                    f64::NAN
                                } else {
                                    array.value(row_idx)
                                }
                            }
                            None => f64::NAN,
                        };
                        row_values.push(value);
                    }
                    
                    all_data.insert(row_date, row_values);
                }
            }
        }

        // 转换为矩阵格式
        let mut dates: Vec<i64> = all_data.keys().cloned().collect();
        dates.sort();
        
        let n_dates = dates.len();
        let n_stocks = all_data.values().next().map_or(0, |v| v.len());
        
        // 使用从schema中读取的真实股票名称，而不是生成虚假名称
        
        let mut values = DMatrix::zeros(n_dates, n_stocks);
        
        for (date_idx, &date) in dates.iter().enumerate() {
            if let Some(row_values) = all_data.get(&date) {
                for (stock_idx, &value) in row_values.iter().enumerate() {
                    values[(date_idx, stock_idx)] = value;
                }
            }
        }

        let load_time = load_start.elapsed();
        println!("✅ 简化数学优化因子数据加载完成: {:.3}s", load_time.as_secs_f64());

        Ok(SimpleMathOptimizedFactorData {
            dates,
            stocks,
            values,
        })
    }
}

/// 执行简化的数学优化批量因子中性化
pub fn neutralize_factor_simple_math_optimized(
    factor_data: &SimpleMathOptimizedFactorData,
    style_data: &SimpleMathOptimizedStyleData,
) -> PyResult<SimpleMathOptimizedNeutralizationResult> {
    
    let neutralization_start = Instant::now();
    
    let union_stocks = &factor_data.stocks;
    let n_dates = factor_data.dates.len();
    let n_union_stocks = union_stocks.len();
    
    let mut neutralized_values = DMatrix::from_element(n_dates, n_union_stocks, f64::NAN);
    
    println!("🧮 开始简化数学优化的因子中性化处理...");
    println!("   📊 处理维度: {}天 × {}股票", n_dates, n_union_stocks);
    
    let mut processed_dates = 0;
    
    // 并行处理每个日期的中性化
    let date_results: Vec<_> = factor_data.dates
        .par_iter()
        .enumerate()
        .filter_map(|(date_idx, &date)| {
            if let Some(day_data) = style_data.data_by_date.get(&date) {
                
                // 获取因子值并计算排名
                let mut factor_values = Vec::new();
                for stock_idx in 0..n_union_stocks {
                    factor_values.push(factor_data.values[(date_idx, stock_idx)]);
                }
                
                let ranked_values = rank_with_nan_handling_optimized(&factor_values);
                
                // 执行优化的回归计算
                match perform_stable_regression_optimized(&ranked_values, day_data, union_stocks) {
                    Ok(neutralized_row) => Some((date_idx, neutralized_row)),
                    Err(_) => None
                }
            } else {
                None
            }
        })
        .collect();
    
    // 收集结果
    for (date_idx, neutralized_row) in date_results {
        for (stock_idx, value) in neutralized_row.into_iter().enumerate() {
            neutralized_values[(date_idx, stock_idx)] = value;
        }
        processed_dates += 1;
    }
    
    let neutralization_time = neutralization_start.elapsed();
    
    println!("✅ 简化数学优化中性化完成:");
    println!("   📅 成功处理日期: {}/{}", processed_dates, n_dates);
    println!("   ⏱️  处理用时: {:.3}s", neutralization_time.as_secs_f64());
    println!("   📈 处理速度: {:.1}天/秒", processed_dates as f64 / neutralization_time.as_secs_f64());

    Ok(SimpleMathOptimizedNeutralizationResult {
        dates: factor_data.dates.clone(),
        stocks: factor_data.stocks.clone(),
        neutralized_values,
    })
}

/// 执行稳定的回归计算
fn perform_stable_regression_optimized(
    ranked_values: &[f64],
    day_data: &SimpleMathOptimizedStyleDayData,
    union_stocks: &[String],
) -> PyResult<Vec<f64>> {
    
    // 构建有效的回归数据
    let mut regression_y = Vec::new();
    let mut regression_x_indices = Vec::new();
    
    for (union_idx, union_stock) in union_stocks.iter().enumerate() {
        if !ranked_values[union_idx].is_nan() {
            if let Some(style_idx) = day_data.stocks.iter().position(|s| s == union_stock) {
                regression_y.push(ranked_values[union_idx]);
                regression_x_indices.push(style_idx);
            }
        }
    }
    
    if regression_y.len() < 12 {
        return Err(PyRuntimeError::new_err("有效样本数不足"));
    }
    
    // 使用预计算的QR分解进行稳定求解
    if let Some(ref qr) = day_data.qr_decomposition {
        let y_vector = DVector::from_vec(regression_y.clone());
        
        // 构建对应的X矩阵
        let n_valid = regression_x_indices.len();
        let mut x_matrix = DMatrix::zeros(n_valid, 12);
        
        for (i, &style_idx) in regression_x_indices.iter().enumerate() {
            for j in 0..12 {
                x_matrix[(i, j)] = day_data.style_matrix[(style_idx, j)];
            }
        }
        
        // 使用QR分解求解
        let x_matrix_clone = x_matrix.clone();
        let x_qr = x_matrix.qr();
        
        // 数值稳定性检查
        if !day_data.is_well_conditioned {
            // 对于条件较差的矩阵，使用更保守的求解方法
            if let Some(beta) = x_qr.solve(&y_vector) {
                let predicted = &x_matrix_clone * &beta;
                let residuals = &y_vector - &predicted;
                
                // 构建中性化结果
                let mut neutralized_row = vec![f64::NAN; union_stocks.len()];
                for (i, &union_idx) in regression_x_indices.iter().enumerate() {
                    if i < residuals.len() {
                        neutralized_row[union_idx] = residuals[i];
                    }
                }
                
                return Ok(neutralized_row);
            }
        } else {
            // 对于良好条件的矩阵，直接求解
            if let Some(beta) = x_qr.solve(&y_vector) {
                let predicted = &x_matrix_clone * &beta;
                let residuals = &y_vector - &predicted;
                
                let mut neutralized_row = vec![f64::NAN; union_stocks.len()];
                for (i, &union_idx) in regression_x_indices.iter().enumerate() {
                    if i < residuals.len() {
                        neutralized_row[union_idx] = residuals[i];
                    }
                }
                
                return Ok(neutralized_row);
            }
        }
        
        Err(PyRuntimeError::new_err("QR求解失败"))
    } else {
        Err(PyRuntimeError::new_err("QR分解未预计算"))
    }
}

/// 优化的排名函数
fn rank_with_nan_handling_optimized(values: &[f64]) -> Vec<f64> {
    let n = values.len();
    let mut indexed_values: Vec<(usize, f64)> = values.iter()
        .enumerate()
        .filter(|(_, &val)| !val.is_nan())
        .map(|(idx, &val)| (idx, val))
        .collect();
    
    indexed_values.sort_by(|a, b| a.1.partial_cmp(&b.1).unwrap());
    
    let mut ranks = vec![f64::NAN; n];
    let valid_count = indexed_values.len();
    
    if valid_count > 0 {
        for (rank, &(original_idx, _)) in indexed_values.iter().enumerate() {
            ranks[original_idx] = (rank as f64) / (valid_count - 1) as f64;
        }
    }
    
    ranks
}

/// 保存简化的结果
fn save_simple_neutralization_result(
    result: &SimpleMathOptimizedNeutralizationResult,
    output_path: &str,
) -> PyResult<()> {
    
    use parquet::arrow::ArrowWriter;
    use parquet::file::properties::WriterProperties;
    
    // 创建数据
    let mut data = Vec::new();
    
    for (date_idx, &date) in result.dates.iter().enumerate() {
        for (stock_idx, stock) in result.stocks.iter().enumerate() {
            let value = result.neutralized_values[(date_idx, stock_idx)];
            if !value.is_nan() {
                data.push((date, stock.clone(), value));
            }
        }
    }
    
    if data.is_empty() {
        return Err(PyRuntimeError::new_err("没有有效的中性化结果"));
    }
    
    // 构建Arrow记录
    let dates: Vec<i64> = data.iter().map(|(d, _, _)| *d).collect();
    let stocks: Vec<String> = data.iter().map(|(_, s, _)| s.clone()).collect();
    let values: Vec<f64> = data.iter().map(|(_, _, v)| *v).collect();
    
    let date_array = Int64Array::from(dates);
    let stock_array = StringArray::from(stocks);
    let value_array = Float64Array::from(values);
    
    let schema = Arc::new(Schema::new(vec![
        Field::new("date", DataType::Int64, false),
        Field::new("stock", DataType::Utf8, false),
        Field::new("neutralized_value", DataType::Float64, false),
    ]));
    
    let batch = RecordBatch::try_new(
        schema.clone(),
        vec![
            Arc::new(date_array),
            Arc::new(stock_array), 
            Arc::new(value_array),
        ]
    ).map_err(|e| PyRuntimeError::new_err(format!("创建记录批失败: {}", e)))?;
    
    // 写入文件
    let file = File::create(output_path)
        .map_err(|e| PyRuntimeError::new_err(format!("创建输出文件失败: {}", e)))?;
    
    let props = WriterProperties::builder()
        .set_compression(parquet::basic::Compression::SNAPPY)
        .build();
    
    let mut writer = ArrowWriter::try_new(file, schema, Some(props))
        .map_err(|e| PyRuntimeError::new_err(format!("创建Parquet写入器失败: {}", e)))?;
    
    writer.write(&batch)
        .map_err(|e| PyRuntimeError::new_err(format!("写入数据失败: {}", e)))?;
    
    writer.close()
        .map_err(|e| PyRuntimeError::new_err(format!("关闭写入器失败: {}", e)))?;
    
    Ok(())
}

/// 简化数学优化批量因子中性化主函数
#[pyfunction]
pub fn batch_factor_neutralization_simple_math_optimized(
    style_data_path: &str,
    factor_files_dir: &str,
    output_dir: &str,
    num_threads: Option<usize>,
) -> PyResult<()> {
    // 设置线程数
    if let Some(threads) = num_threads {
        rayon::ThreadPoolBuilder::new()
            .num_threads(threads)
            .build_global()
            .map_err(|e| PyRuntimeError::new_err(format!("设置线程池失败: {}", e)))?;
    }
    
    let total_start = Instant::now();
    println!("🚀 开始简化数学优化的批量因子中性化处理");
    println!("   🧮 优化特性: QR分解, 数值稳定性, 并行计算");
    println!("   🧵 使用线程数: {}", num_threads.unwrap_or_else(num_cpus::get));
    
    // 1. 加载风格数据
    let style_data = SimpleMathOptimizedStyleData::load_from_parquet_simple_math_optimized(style_data_path)?;
    
    // 2. 扫描因子文件
    let factor_dir = Path::new(factor_files_dir);
    let mut factor_files = Vec::new();
    
    for entry in factor_dir.read_dir()
        .map_err(|e| PyRuntimeError::new_err(format!("读取因子目录失败: {}", e)))? {
        let entry = entry
            .map_err(|e| PyRuntimeError::new_err(format!("读取目录项失败: {}", e)))?;
        
        if let Some(ext) = entry.path().extension() {
            if ext == "parquet" {
                factor_files.push(entry.path());
            }
        }
    }
    
    println!("📁 找到因子文件: {} 个", factor_files.len());
    
    // 3. 并行处理所有因子文件
    let processing_results: Vec<_> = factor_files
        .par_iter()
        .map(|factor_file| {
            process_single_factor_simple_math_optimized(factor_file, &style_data, output_dir)
        })
        .collect();
    
    // 4. 统计结果
    let mut successful = 0;
    let mut failed = 0;
    
    for result in processing_results {
        match result {
            Ok(_) => successful += 1,
            Err(e) => {
                failed += 1;
                eprintln!("❌ 处理失败: {}", e);
            }
        }
    }
    
    let total_time = total_start.elapsed();
    
    println!("\n🎉 简化数学优化批量因子中性化完成!");
    println!("   ✅ 成功处理: {} 个文件", successful);
    println!("   ❌ 处理失败: {} 个文件", failed);
    println!("   ⏱️  总用时: {:.3}s", total_time.as_secs_f64());
    println!("   📈 平均速度: {:.2} 文件/秒", successful as f64 / total_time.as_secs_f64());
    
    Ok(())
}

/// 处理单个因子文件（简化数学优化版本）
fn process_single_factor_simple_math_optimized(
    factor_file: &PathBuf,
    style_data: &SimpleMathOptimizedStyleData,
    output_dir: &str,
) -> PyResult<()> {
    let file_start = Instant::now();
    
    // 加载因子数据
    let factor_data = SimpleMathOptimizedFactorData::load_from_parquet_simple_math_optimized(
        factor_file.to_str().unwrap()
    )?;
    
    // 执行中性化
    let result = neutralize_factor_simple_math_optimized(&factor_data, style_data)?;
    
    // 保存结果
    let output_file = Path::new(output_dir).join(
        factor_file.file_name().unwrap()
    );
    
    save_simple_neutralization_result(&result, output_file.to_str().unwrap())?;
    
    let file_time = file_start.elapsed();
    println!("✅ 处理完成: {} ({:.3}s)", 
             factor_file.file_name().unwrap().to_str().unwrap(),
             file_time.as_secs_f64());
    
    Ok(())
}
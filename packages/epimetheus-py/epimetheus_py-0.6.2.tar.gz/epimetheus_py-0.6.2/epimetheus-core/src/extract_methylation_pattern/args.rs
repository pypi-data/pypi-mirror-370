use clap::Parser;

#[derive(Parser, Debug, Clone)]
pub struct MethylationPatternArgs {
    #[arg(short, long, required = true, help = "Path to pileup.")]
    pub pileup: String,

    #[arg(short, long, required = true, help = "Path to assembly.")]
    pub assembly: String,

    #[arg(
        short,
        long,
        required = true,
        help = "Path to output file. Must be .tsv."
    )]
    pub output: String,

    #[arg(short, long, default_value_t = 1, help = "Number of parallel tasks.")]
    pub threads: usize,

    #[arg(short, long, required = true, num_args(1..), help = "Supply chain of motifs as <motif>_<mod_type>_<mod_position>. Example: '-m GATC_a_1 RGATCY_a_2'")]
    pub motifs: Option<Vec<String>>,

    #[arg(
        long,
        default_value_t = 3,
        help = "Minimum valid read coverage for calculating methylation."
    )]
    pub min_valid_read_coverage: u32,

    #[arg(
        long,
        default_value_t = 1000,
        help = "Number of contigs to process at a time. Higher number will use more RAM."
    )]
    pub batch_size: usize,

    #[arg(
        long,
        default_value_t = 0.8,
        help = "Required fraction of valid coverage relative to different read mapping. N_valid_cov / (N_valid_cov + N_diff)"
    )]
    pub min_valid_cov_to_diff_fraction: f32,
    // #[arg(long, default_value_t = 0.9, help = "Maximum failed fraction relative to valid coverage. N_valid_cov / (N_valid_cov + N_diff)")]
    // pub : f32,
    #[arg(
        long,
        default_value_t = false,
        help = "Allow epimetheus to continue if a contig in the pileup is not present in the assembly"
    )]
    pub allow_assembly_pileup_mismatch: bool,
}

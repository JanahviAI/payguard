// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract PayGuardEscrow {
    enum JobStatus {
        None,
        Funded,
        Released,
        Refunded
    }

    struct Job {
        address client;
        address freelancer;
        uint256 amount;
        JobStatus status;
    }

    address public immutable owner;
    mapping(uint256 => Job) public jobs;

    event JobCreated(uint256 indexed jobId, address indexed client, address indexed freelancer, uint256 amount);
    event PaymentReleased(uint256 indexed jobId, address indexed freelancer, uint256 amount);
    event PaymentRefunded(uint256 indexed jobId, address indexed client, uint256 amount);

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    function createJob(uint256 jobId, address freelancer) external payable {
        require(freelancer != address(0), "Invalid freelancer");
        require(msg.value > 0, "Amount required");
        require(jobs[jobId].client == address(0), "Job exists");

        jobs[jobId] = Job({
            client: msg.sender,
            freelancer: freelancer,
            amount: msg.value,
            status: JobStatus.Funded
        });

        emit JobCreated(jobId, msg.sender, freelancer, msg.value);
    }

    function release(uint256 jobId) external onlyOwner {
        Job storage job = jobs[jobId];
        require(job.client != address(0), "Job not found");
        require(job.status == JobStatus.Funded, "Job not funded");

        job.status = JobStatus.Released;
        (bool sent, ) = payable(job.freelancer).call{value: job.amount}("");
        require(sent, "Transfer failed");

        emit PaymentReleased(jobId, job.freelancer, job.amount);
    }

    function refund(uint256 jobId) external onlyOwner {
        Job storage job = jobs[jobId];
        require(job.client != address(0), "Job not found");
        require(job.status == JobStatus.Funded, "Job not funded");

        job.status = JobStatus.Refunded;
        (bool sent, ) = payable(job.client).call{value: job.amount}("");
        require(sent, "Transfer failed");

        emit PaymentRefunded(jobId, job.client, job.amount);
    }
}

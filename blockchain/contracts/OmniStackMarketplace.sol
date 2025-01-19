// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract OmniStackMarketplace is ReentrancyGuard, Ownable {
    // Structs
    struct AIModule {
        address creator;
        string metadata;
        uint256 price;
        bool isActive;
        uint256 rating;
        uint256 numRatings;
    }

    // State variables
    mapping(uint256 => AIModule) public modules;
    uint256 public nextModuleId;
    uint256 public platformFee = 25; // 2.5%
    
    // Events
    event ModuleCreated(
        uint256 indexed moduleId,
        address indexed creator,
        string metadata,
        uint256 price
    );
    
    event ModulePurchased(
        uint256 indexed moduleId,
        address indexed buyer,
        uint256 price
    );
    
    event ModuleRated(
        uint256 indexed moduleId,
        address indexed rater,
        uint256 rating
    );

    constructor() {
        nextModuleId = 1;
    }

    function createModule(
        string memory metadata,
        uint256 price
    ) external returns (uint256) {
        require(price > 0, "Price must be greater than 0");
        
        uint256 moduleId = nextModuleId++;
        
        modules[moduleId] = AIModule({
            creator: msg.sender,
            metadata: metadata,
            price: price,
            isActive: true,
            rating: 0,
            numRatings: 0
        });
        
        emit ModuleCreated(moduleId, msg.sender, metadata, price);
        
        return moduleId;
    }

    function purchaseModule(
        uint256 moduleId
    ) external payable nonReentrant {
        AIModule storage module = modules[moduleId];
        require(module.isActive, "Module is not active");
        require(msg.value >= module.price, "Insufficient payment");
        
        // Calculate platform fee
        uint256 fee = (module.price * platformFee) / 1000;
        uint256 creatorPayment = module.price - fee;
        
        // Transfer payments
        payable(module.creator).transfer(creatorPayment);
        payable(owner()).transfer(fee);
        
        // Refund excess payment
        if (msg.value > module.price) {
            payable(msg.sender).transfer(msg.value - module.price);
        }
        
        emit ModulePurchased(moduleId, msg.sender, module.price);
    }

    function rateModule(
        uint256 moduleId,
        uint256 rating
    ) external {
        require(rating >= 1 && rating <= 5, "Rating must be between 1 and 5");
        AIModule storage module = modules[moduleId];
        require(module.isActive, "Module is not active");
        
        module.rating = ((module.rating * module.numRatings) + rating) / (module.numRatings + 1);
        module.numRatings++;
        
        emit ModuleRated(moduleId, msg.sender, rating);
    }

    function updateModulePrice(
        uint256 moduleId,
        uint256 newPrice
    ) external {
        require(modules[moduleId].creator == msg.sender, "Not module creator");
        require(newPrice > 0, "Price must be greater than 0");
        
        modules[moduleId].price = newPrice;
    }

    function deactivateModule(uint256 moduleId) external {
        require(modules[moduleId].creator == msg.sender, "Not module creator");
        modules[moduleId].isActive = false;
    }

    function setPlatformFee(uint256 newFee) external onlyOwner {
        require(newFee <= 100, "Fee too high"); // Max 10%
        platformFee = newFee;
    }

    function getModule(
        uint256 moduleId
    ) external view returns (AIModule memory) {
        return modules[moduleId];
    }
}

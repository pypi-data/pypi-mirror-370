//
//  IrisCodecCache.hpp
//  Iris
//
//  Created by Ryan Landvater on 4/14/24.
//

#ifndef IrisCodecCache_hpp
#define IrisCodecCache_hpp
namespace IrisCodec {
class __INTERNAL__Cache : protected __INTERNAL__Slide {
    CacheEncoding                   _codec = CACHE_ENCODING_UNDEFINED;
public:
    explicit __INTERNAL__Cache      (const CacheCreateInfo&, const File&);
    __INTERNAL__Cache               (const __INTERNAL__Cache&) = delete;
    __INTERNAL__Cache& operator =   (const __INTERNAL__Cache&) = delete;
    
    Result store_entry              (const CacheStoreInfo&);
};
}

#endif /* IrisCodecArchive_hpp */
